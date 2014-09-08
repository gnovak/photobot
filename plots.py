# code to produce plots.

def ps_plot(good, bad):

    pl.clf()

    for ims, col in ((good, 'green'), 
                     (bad, 'red')):
        pss = []
        sigs = []
        for im in ims:
            kk, ps, sig = log_power_spect(im)
            pss.append(ps)
            sigs.append(sig)
        pss = np.array(pss)
        sigs = np.array(sigs)
        
        pl.errorbar(kk, pss.mean(axis=0), pss.std(axis=0), color=col)
        #pl.errorbar(kk, sigs.mean(axis=0), sigs.std(axis=0), color=col)

def color_dist_plot(good, bad, bins=None, col=lambda x: x):
    # plot mean, variance, and individual lines of color dists
    if bins is None: bins = np.linspace(0,255,30)
    result = []
    for idx in (0,1,2):
        r1 = []
        for ims in (good, bad):
            r2 = []
            for im in ims:
                the_im = col(im)[:,:,idx].ravel()
                ys, xs, junk = pl.hist(the_im, bins)
                r2.append(ys)
            r1.append(r2)
        result.append(r1)

    # Now draw the actual plot
    pl.clf()
    for r1, idx in zip(result, (0,1,2)):
        pl.subplot(3,1,idx)
        for r2,the_col in zip(r1, ('green', 'red')):
            r2 = np.array(r2)
            # Linear mean
            # pl.semilogy(nu.ave(bins), r2.mean(axis=0), 
            #            color=the_col)
            # Geometric mean
            # pl.plot(nu.ave(bins), np.log10(r2.clip(1, None)).mean(axis=0), 
            #             color=the_col)
            # Linear mean + std
            # pl.errorbar(nu.ave(bins), r2.mean(axis=0), r2.std(axis=0), 
            #             color=the_col)
            # pl.yscale('log')
            # pl.ylim(10,None)
            # Mean + std in log space

            pl.errorbar(nu.ave(bins), np.log10(r2.clip(1,None)).mean(axis=0), 
                       np.log10(r2.clip(1,None)).std(axis=0), 
                       color=the_col)
            #pl.xlim(0,260)
            # for r3 in r2:
            #     pl.plot(nu.ave(bins), r3, lw='1', color=the_col)
