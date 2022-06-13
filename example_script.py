from dfobserve.observing import Observation
#from observepy.utils.MountUtils import HomeMount 

#========================  Setup  ====================================

# Make Observation object for each target
# Contains core info: target name, exp time, iterations, whether to focus

m82 = Observation(target='M 82',
                exptime=3600,
                iterations=2,
                do_focus=True,
                min_altitude=35,
                )

# Add some configurations to the observation
# contains info about dither and off band exp stuff
m82.configure_observation(wait_until='target_rise',
                    dither_angle=15, # dither angle from target center
                    dither_pattern=[5,3,7,1,9,2,8,4,6], # dither pattern on grid
                    randomize_dithers=True, #choose random dither pattern
                    off_band_exptime=600, # 20 sec exposures for the off bands
                    off_band_throughout=True)

# contains info about darks and flats 

m82.configure_calibrations(n_darks=1,
                            dark_exptime=60,
                            take_darks='after',
                            n_flats=1,
                            flat_exptime=60,
                            take_flats='all')

# Contains info about standards 
m82.configure_standards(use='nearest',
                        n_standards=1,
                        when='all')


# Set the tilts of the science filters
m82.set_tilts('halpha',14.5)
m82.set_tilts('oiii',12.6)


# m81 = Observation(target='M81',
#                 exptime=3600,
#                 iterations=2,
#                 do_focus=False,
#                 min_altitude=35)
# m81.configure_observation(wait_until=None, #go right after the previous
#                     n_darks=0, # no darks with obs of target
#                     n_flats=2, # 2 flats after obs completes
#                     dark_between=False, # no darks between dither seqs
#                     flat_between=False, # no flats between dither seqs
#                     dither_angle=15, # dither angle from target center (arcmin)
#                     dither_pattern=[5,3,7,1,9,2,8,4,6], # dither pattern on grid (only 5,3 will be used)
#                     off_band_exptime=20, # 20 sec exposures for the off bands
#                     )
#m81.set_tilts('halpha',14.5)
#m81.set_tilts('oiii',12.6)


#=================  Observing Procedures  ====================================
#obslist = [m82,m81]

# For now, observe() calls are made in sequence. It is the user's responsibility
# to plan so that obs can finish. However, in the future, I plan to add the ability
# to supply an AutoObserve class with a list of targets along with priorities etc., 
# so it will know to bail out of one target to be sure to get another (etc). 
#m82.observe() 

#m81.observe() 

#================== End Of Night Procedures ====================
#HomeMount() #send the mount home
#morning_darks(obslist,5) #for each obj (with its exptime), take 5 darks.
#shutdown() # shut everything down
