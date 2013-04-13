C
C     Basic parameters of the model atmosphere
C
      COMMON/MODELP/DM(MDEPTH),
     *              TEMP(MDEPTH),
     *              ELEC(MDEPTH),
     *              DENS(MDEPTH),
     *              ZD(MDEPTH),
     *              VTURB(MDEPTH),VTB,
     *              ABSTD(MDEPTH),
     *              ABSTDW(MFREQC,MDEPTH),
     *              POPUL(MLEVEL,MDEPTH),
     *              POPREL(MLEVEL,MDEPTH),
     *              DMR0(MDEPTH),          
     *              DMRP(MDEPTH),          
     *              SBF(MLEVEL),
     *              USUM(MIOEX),
     *              WOP(MLEVEL,MDEPTH),
     *              WNHINT(NLMX,MDEPTH),
     *              WNHE2(NLMX,MDEPTH),
     *              RRR(MDEPTH,MION,MATOM),
     *              JT(MDEPTH),
     *              TI0(MDEPTH),
     *              TI1(MDEPTH),
     *              TI2(MDEPTH)
      COMMON/MOLPAR/RRMOL(MMOLEC,MDEPTH),
     *              DOPMOL(MMOLEC,MDEPTH),
     *              AMMOL(MMOLEC),
     *              CMOL(MMOLEC),
     *              anh2(mdepth),anch(mdepth),anoh(mdepth),
     *              anhm(mdepth)
C
      COMMON/OPACAT/OPATM(MATOM,MFREQ,MDEPTH),
     *              EMATM(MATOM,MFREQ,MDEPTH),
     *              OPATML(MATOM,MFREQ),
     *              GRADAT(MATOM,MDEPTH),
     *              GRADFA(MATOM,MDEPTH),	
     *              POPAT(MATOM,MDEPTH),
     *              DGRAD0(MATOM,MATOM,MDEPTH),
     *              DGRADP(MATOM,MATOM,MDEPTH)
C
      COMMON/RADFLD/RAD(MFREQ,MDEPTH),
c    *              FAK(MFREQ,MDEPTH),
c    *              ALI(MFREQ,MDEPTH),
c    *              FLXH(MFREQ,MDEPTH),
     *              RAD0(MFREQ,MDEPTH),
     *              FLX0(MFREQ,MDEPTH),
     *              flxt(mdepth),
     *              flxi(mdepth)

