#!/usr/bin/env python

import sys, os
import glob
import numpy as np
import astropy.io.fits as pyfits


# 11 12 13 14 15
# 16  2  3  4 17
# 18  5  6  7 19
# 20  8  9 10 21
# 22 23 24 25 26
ioff_list = [
    [11, 12, 13, 14, 15],
    [16,  2,  3,  4, 17],
    [18,  5,  6,  7, 19],
    [20,  8,  9, 10, 21],
    [22, 23, 24, 25, 26],
]    


if __name__=="__main__" :

    if len(sys.argv)!=3 :
        print("(Usage) genevtfits (dirname) (output filename)")
        sys.exit()

    dirname  = sys.argv[1]
    outfname = sys.argv[2]

    if os.path.isfile(outfname) :
        print("(Error) output filename %s already exists."%(outfname))
        sys.exit()
    

    ### Default parameters ####
    telescop = "HIZGUNDAM"
    instrume = "EAGLE"


    evthr = 100  
    spthr = 10   
    
    nxypixels = 2048  
    nchannels = 4096
    

    flist = sorted(glob.glob('%s/p???????.bin'%(dirname))) #[:20]
    #print(flist)
    
    dt = np.dtype(np.int16)
    
    
    clklist = []
    xlist = []
    ylist = []
    adc5x5list = []
    sum5x5avglist = []
    phasumlist = []
    nhitpixlist  = []
    
    for fname in flist :
        buf = np.fromfile(open(fname), dtype=dt)
        nbuf = len(buf)
        ndata = int((nbuf-3)/27)
        print("### filename=%s nbuf=%d  ndata=%d"%(fname, nbuf, ndata))
    
        buf0  = np.int32(buf[0])
        buf1  = np.int32(buf[1])
        buf0 += (buf0<0)*0x10000
        buf1 += (buf1<0)*0x10000
        seqclk = (buf0|(buf1<< 16))
    
        #print("Header: 0x%04x 0x%04x 0x%04x"%(buf[0],buf[1],buf[2]))
        print("Header: 0x%04x 0x%04x 0x%04x, seqclk=%d  buf2=%d"%(buf0, buf1, buf[2], seqclk, buf[2]))
        #continue
        
        for idat in range(ndata) :
            i0 = 3+idat*27
            xpos = buf[i0]
            ypos = buf[i0+1]
            #sum5x5avg = buf[i0+11:i0+27].sum()/16.0
    
            adc5x5 = buf[i0+2:i0+27]
            adcsum = adc5x5.sum()
            sum5x5avg = adc5x5[9:25].sum()/16.0
            pha5x5 = adc5x5+sum5x5avg
            hitpix = pha5x5>spthr
            nhitpix = int((hitpix*1).sum())
            phasum = pha5x5[hitpix].sum()
            
            print("%d x=%d, y=%d, adcsum=%d, sum5x5avg=%.2lf, phasum=%.2lf, nhitpix=%d"%(idat, xpos, ypos, adcsum, sum5x5avg, phasum, nhitpix))
    
            if idat < 5 :
                for iy in range(5) :
                    outstr=""
                    for ix in range(5) :
                        ioff = ioff_list[iy][ix]
                        #outstr+=" %4d"%(buf[i0+ioff])
                        outstr+=" %4d"%(adc5x5[ioff-2])
                    print(outstr)
                
    
            clklist.append(seqclk)
            xlist.append(xpos)
            ylist.append(ypos)
            adc5x5list.append(adc5x5)
            sum5x5avglist.append(sum5x5avg)
            phasumlist.append(phasum)
            nhitpixlist.append(nhitpix)
    
    
    
    c1 = pyfits.Column(name='SEQCLK', array=clklist,    format='1J', unit='')
    c2 = pyfits.Column(name='X',      array=xlist,      format='1I',  unit='pixel')
    c3 = pyfits.Column(name='Y',      array=ylist,      format='1I',  unit='pixel')
    c4 = pyfits.Column(name='PHASUM', array=phasumlist, format='1E',  unit='channel')
    c5 = pyfits.Column(name='ADC5x5', array=adc5x5list, format='25I', unit='channel')
    c6 = pyfits.Column(name='NHITPIX', array=nhitpixlist, format='1I', unit='')
    
    evthdu = pyfits.BinTableHDU.from_columns([c1, c2, c3, c4, c5, c6])


    evthdu.header["EXTNAME"]=("EVENTS", "name of this binary table extension")
    evthdu.header["TELESCOP"]=(telescop, "Telescope (mission) name")
    evthdu.header["INSTRUME"]=(instrume, "Instrument name")
    
    evthdu.header["TLMIN2"]=(0,           "Minimum value for X column")
    evthdu.header["TLMAX2"]=(nxypixels-1, "Maximum value for X column")
    evthdu.header["TLMIN3"]=(0,           "Minimum value for Y column")
    evthdu.header["TLMAX3"]=(nxypixels-1, "Maximum value for Y column")
        
    evthdu.writeto(outfname)
    print("Event file = %s has been created"%(outfname))
    
