import numpy as np
import matplotlib.pyplot as plt
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel, ConstantKernel
import os
import csv
import time

import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D

# Function for converting time to formatted string
def convert_time(t):
    minutes = np.floor((t/3600.0) * 60)
    seconds = np.ceil(((t/3600.0) * 60 - minutes) * 60)
    if (minutes >= 1):
        minutes = np.floor(t/60.0)
        seconds = np.ceil((t/60.0 - minutes) * 60)
        t_str = str(int(minutes)).rjust(2) + 'm  ' + \
                str(int(seconds)).rjust(2) + 's'
    else:
        seconds = (t/60.0 - minutes) * 60
        t_str = str(seconds) + 's'
    return t_str

# Define function for removing axes from MatPlotLib plots
def remove_axes(ax):
    # make the panes transparent
    ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    # make the grid lines transparent
    ax.xaxis._axinfo["grid"]['color'] =  (1,1,1,0)
    ax.yaxis._axinfo["grid"]['color'] =  (1,1,1,0)
    ax.zaxis._axinfo["grid"]['color'] =  (1,1,1,0)
    # remove axes
    ax._axis3don = False


# Plot results of CppGPs, SciKit Learn, and GPyTorch
def main():

    # Specify whether or not to compare SciKit Learn results
    USE_SciKit_Learn = True

    # Specify whether or not to compare GPyTorch results
    USE_GPyTorch = False
    
    # First determine the dimension of the input values
    filename = "predictions.csv"
    with open(filename, "r") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        row = next(csvreader)
        nonInputLength = 3
        inputDim = len(row) - nonInputLength

    # Get prediction data
    filename = "predictions.csv"
    inVals = []; trueVals = []; predMean = []; predStd = []
    with open(filename, "r") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in csvreader:

            if inputDim == 2:
                i1, i2, t, m, v = row
                inVals.append([i1,i2])
            else:
                i, t, m, v = row
                inVals.append(i)
                
            trueVals.append(t)
            predMean.append(m)
            predStd.append(v)
    inVals = np.array(inVals).astype(np.float64)
    trueVals = np.array(trueVals).astype(np.float64)
    predMean = np.array(predMean).astype(np.float64)
    predStd = np.array(predStd).astype(np.float64)

    ## Get observation data
    filename = "observations.csv"
    obsX = []; obsY = []
    with open(filename, "r") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in csvreader:
            if inputDim == 2:
                x1, x2, y = row
                obsX.append([x1,x2])
            else:
                x, y = row
                obsX.append(x)
            obsY.append(y)
    obsX = np.array(obsX).astype(np.float64)
    obsY = np.array(obsY).astype(np.float64)



    if inputDim == 1:
        # Get posterior samples
        filename = "samples.csv"
        samples = []
        with open(filename, "r") as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in csvreader:
                vals = np.array(row)
                samples.append(vals)
        samples = np.array(samples).astype(np.float64)
    
    filename = "NLML.csv"
    NLML_tmp = []
    with open(filename, "r") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in csvreader:
            vals = np.array(row, dtype=np.float32)
            NLML_tmp.append(vals)
    NLML = NLML_tmp[0][0]

    
            
    if USE_SciKit_Learn:

        SciKit_Learn_results_dir = "./SciKit_Learn_Results/"
        
        # Get SciKit Learn prediction data
        filename = os.path.join(SciKit_Learn_results_dir, "predMean.npy")
        skl_predMean = np.load(filename)

        filename = os.path.join(SciKit_Learn_results_dir, "predStd.npy")
        skl_predStd = np.load(filename)
        
        if inputDim == 1:
            # Get posterior samples
            filename = os.path.join(SciKit_Learn_results_dir, "samples.npy")
            skl_samples = np.load(filename)

        filename = os.path.join(SciKit_Learn_results_dir, "NLML.npy")
        skl_NLML = np.load(filename)


    if USE_GPyTorch:

        GPyTorch_results_dir = "./GPyTorch_Results/"
        
        # Get GPyTorch prediction data
        filename = os.path.join(GPyTorch_results_dir, "predMean.npy")
        gpy_predMean = np.load(filename)

        filename = os.path.join(GPyTorch_results_dir, "predStd.npy")
        gpy_predStd = np.load(filename)
        
        if inputDim == 1:
            # Get posterior samples
            filename = os.path.join(GPyTorch_results_dir, "samples.npy")
            gpy_samples = np.load(filename)
            gpy_samples = np.transpose(gpy_samples,[1,0])

        filename = os.path.join(GPyTorch_results_dir, "NLML.npy")
        gpy_NLML = np.load(filename)
            
        
            

    ###                          ###
    ###       DISPLAY NLML       ###
    ###                          ###


    print("\n")
    print("CppGPs NLML:        {:.4f}".format(NLML))
    if USE_SciKit_Learn:
        print("\nSciKit Learn NLML:  {:.4f}".format(skl_NLML))
    if USE_GPyTorch:
        print("\nGPyTorch NLML:      {:.4f}".format(gpy_NLML))
    print("\n")
    
    
        
    ###                          ###
    ###       PLOT RESULTS       ###
    ###                          ###

    if inputDim == 1:

        """ ONE-DIMENSIONAL PLOTS """
        

        # Plot SciKit Learn results
        if USE_SciKit_Learn:
            plt.figure()
            plt.plot(inVals, skl_predMean, 'C0', linewidth=2.0)
            alpha = 0.075
            for k in [1,2,3]:
                plt.fill_between(inVals, skl_predMean-k*skl_predStd, skl_predMean+k*skl_predStd, where=1 >= 0, facecolor="C0", alpha=alpha, interpolate=True, label=None)
            plt.plot(inVals, trueVals, 'C1', linewidth=1.0, linestyle="dashed")
            alpha_scatter = 0.5
            plt.scatter(obsX, obsY, alpha=alpha_scatter)
            for i in range(0,skl_samples.shape[1]):
                plt.plot(inVals, skl_samples[:,i], 'C0', alpha=0.2, linewidth=1.0, linestyle="dashed")
            plt.suptitle("SciKit Learn Implementation")

        
        # Plot GPyTorch results
        if USE_GPyTorch:
            plt.figure()
            plt.plot(inVals, gpy_predMean, 'C0', linewidth=2.0)
            alpha = 0.075
            for k in [1,2,3]:
                plt.fill_between(inVals, gpy_predMean-k*gpy_predStd, gpy_predMean+k*gpy_predStd, where=1 >= 0, facecolor="C0", alpha=alpha, interpolate=True, label=None)
            plt.plot(inVals, trueVals, 'C1', linewidth=1.0, linestyle="dashed")
            alpha_scatter = 0.5
            plt.scatter(obsX, obsY, alpha=alpha_scatter)
            for i in range(0,gpy_samples.shape[1]):
                plt.plot(inVals, gpy_samples[:,i], 'C0', alpha=0.2, linewidth=1.0, linestyle="dashed")
            plt.suptitle("GPyTorch Implementation")
        

        # CppGPs results
        plt.figure()    
        plt.plot(inVals, predMean, 'C0', linewidth=2.0)
        for k in [1,2,3]:
            plt.fill_between(inVals, predMean-k*predStd, predMean+k*predStd, where=1>=0, facecolor="C0", alpha=alpha, interpolate=True)
        plt.plot(inVals, trueVals, 'C1', linewidth=1.0, linestyle="dashed")
        plt.scatter(obsX, obsY, alpha=alpha_scatter)
        for i in range(0,samples.shape[0]):
            plt.plot(inVals, samples[i,:], 'C0', alpha=0.2, linewidth=1.0, linestyle="dashed")
        plt.suptitle("CppGPs Implementation")    
        plt.show()




    
    
    elif inputDim == 2:

        """ TWO-DIMENSIONAL PLOTS """
        
        # Flatten input values for compatibility with MatPlotLib's tri_surf
        plot_X_flat = []; plot_Y_flat = []
        R = inVals.shape[0]
        for n in range(0,R):
            plot_X_flat.append(inVals[n,0])
            plot_Y_flat.append(inVals[n,1])

        tri_fig = plt.figure()
        tri_ax1 = tri_fig.add_subplot(121, projection='3d')
        linewidth = 0.1
        cmap = "Blues"

        # Plot CppGPs results
        tri_ax1.plot_trisurf(plot_X_flat,plot_Y_flat, predMean, cmap=cmap, linewidth=linewidth, antialiased=True)
        pred_title = "CppGPs"
        tri_ax1.set_title(pred_title, fontsize=24)

        # Plot SciKit Learn results    
        tri_ax2 = tri_fig.add_subplot(122, projection='3d')
        tri_ax2.plot_trisurf(plot_X_flat,plot_Y_flat, mean, cmap=cmap, linewidth=linewidth, antialiased=True)
        soln_title = "SciKit Learn"
        tri_ax2.set_title(soln_title, fontsize=24)

        # Remove axes from plots
        remove_axes(tri_ax1) 
        remove_axes(tri_ax2) 

        # Bind axes for comparison
        def tri_on_move(event):
            if event.inaxes == tri_ax1:
                if tri_ax1.button_pressed in tri_ax1._rotate_btn:
                    tri_ax2.view_init(elev=tri_ax1.elev, azim=tri_ax1.azim)
                elif tri_ax1.button_pressed in tri_ax1._zoom_btn:
                    tri_ax2.set_xlim3d(tri_ax1.get_xlim3d())
                    tri_ax2.set_ylim3d(tri_ax1.get_ylim3d())
                    tri_ax2.set_zlim3d(tri_ax1.get_zlim3d())
            elif event.inaxes == tri_ax2:
                if tri_ax2.button_pressed in tri_ax2._rotate_btn:
                    tri_ax1.view_init(elev=tri_ax2.elev, azim=tri_ax2.azim)
                elif tri_ax2.button_pressed in tri_ax2._zoom_btn:
                    tri_ax1.set_xlim3d(tri_ax2.get_xlim3d())
                    tri_ax1.set_ylim3d(tri_ax2.get_ylim3d())
                    tri_ax1.set_zlim3d(tri_ax2.get_zlim3d())
            else:
                return
            tri_fig.canvas.draw_idle()
        tri_c1 = tri_fig.canvas.mpl_connect('motion_notify_event', tri_on_move)



        """ Zoom in to view predictive uncertainty """
        plot_radius = 0.5
        plot_x_min = -0.125
        plot_y_min = -0.125
        plot_x_max = 0.25

        # Define conditions for including values associated with an input point (x,y)
        def include_conditions(x,y,delta=0.0):
            rad = np.sqrt(np.power(x,2) + np.power(y,2))
            return (x-delta<=plot_x_max) and (x+delta>=plot_x_min) and (y+delta>=plot_y_min) and (rad-delta<=plot_radius)


        # Restrict plots to values corresponding to valid input points
        R = inVals.shape[0]    
        plot_X_zoom = []; plot_Y_zoom = []; predMean_zoom = []
        predMean_plus_std = []; predMean_minus_std = []
        predMean_plus_std2 = []; predMean_minus_std2 = []
        predMean_plus_std3 = []; predMean_minus_std3 = []
        trueVals_zoom = []
        for n in range(0,R):
            x = plot_X_flat[n]
            y = plot_Y_flat[n]
            if include_conditions(x,y,delta=0.025):
                plot_X_zoom.append(x)
                plot_Y_zoom.append(y)
                predMean_zoom.append(predMean[n])
                predMean_plus_std.append( predMean[n] + 1 * predStd[n] )
                predMean_minus_std.append( predMean[n] - 1 * predStd[n] )
                predMean_plus_std2.append( predMean[n] + 2 * predStd[n] )
                predMean_minus_std2.append( predMean[n] - 2 * predStd[n] )
                predMean_plus_std3.append( predMean[n] + 3 * predStd[n] )
                predMean_minus_std3.append( predMean[n] - 3 * predStd[n] )
                trueVals_zoom.append(trueVals[n])


        # Restrict observations to valid input points
        obsX_x_zoom = []; obsX_y_zoom = []; obsY_zoom = []
        for n in range(0, obsX.shape[0]):
            x = obsX[n,0]
            y = obsX[n,1]
            if include_conditions(x,y):
                obsX_x_zoom.append(x)
                obsX_y_zoom.append(y)
                obsY_zoom.append(obsY[n])


        # Initialize plot for assessing predictive uncertainty 
        tri_fig2 = plt.figure()
        tri2_ax1 = tri_fig2.add_subplot(111, projection='3d')


        # Plot Predictive Mean
        linewidth = 0.1; alpha = 0.85
        tri2_ax1.plot_trisurf(plot_X_zoom,plot_Y_zoom, predMean_zoom, cmap=cmap, linewidth=linewidth, antialiased=True, alpha=alpha)


        # One Standard Deviation
        linewidth = 0.075; alpha = 0.2
        tri2_ax1.plot_trisurf(plot_X_zoom,plot_Y_zoom, predMean_plus_std, cmap=cmap, linewidth=linewidth, antialiased=True,alpha=alpha)
        tri2_ax1.plot_trisurf(plot_X_zoom,plot_Y_zoom, predMean_minus_std, cmap=cmap, linewidth=linewidth,antialiased=True,alpha=alpha)

        # Two Standard Deviations
        linewidth = 0.05; alpha = 0.1
        tri2_ax1.plot_trisurf(plot_X_zoom,plot_Y_zoom, predMean_plus_std2, cmap=cmap, linewidth=linewidth,antialiased=True,alpha=alpha)
        tri2_ax1.plot_trisurf(plot_X_zoom,plot_Y_zoom, predMean_minus_std2, cmap=cmap, linewidth=linewidth,antialiased=True,alpha=alpha)

        # Three Standard Deviations
        linewidth = 0.01; alpha = 0.01
        tri2_ax1.plot_trisurf(plot_X_zoom,plot_Y_zoom, predMean_plus_std3, cmap=cmap, linewidth=linewidth,antialiased=True,alpha=alpha)
        tri2_ax1.plot_trisurf(plot_X_zoom,plot_Y_zoom, predMean_minus_std3, cmap=cmap, linewidth=linewidth,antialiased=True,alpha=alpha)

        # Scatter plot of training observations
        alpha = 0.4
        tri2_ax1.scatter(obsX_x_zoom, obsX_y_zoom, obsY_zoom, c='k', marker='o', s=15.0, alpha=alpha)

        # Add title to plot
        plt.suptitle("CppGPs Predictive Uncertainty", fontsize=24)
        
        # Remove axes from plot
        remove_axes(tri2_ax1)

        # Display plots
        plt.show()
    


# Run main() function when called directly
if __name__ == '__main__':
    main()
