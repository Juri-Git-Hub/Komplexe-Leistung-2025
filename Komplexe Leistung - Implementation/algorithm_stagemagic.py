## IMPORTANT: THIS HAS BEEN CHANGED! EVERY POST NOW HAS THE SHAPE ((x, y), (longitude, latitude))
from matplotlib import pyplot as plt


def plotSolution(lines1, lines2):
    # Plot vorbereiten
    plt.figure(figsize=(10, 6))

    # Linien aus der ersten Gruppe plotten
    for line in lines1:
        x_coord, y_coord = zip(*line)
        plt.plot(x_coord, y_coord, label="Line Group 1", color="blue")

    # Linien aus der zweiten Gruppe plotten
    for line in lines2:
        x_coords, y_coords = zip(*line)
        plt.plot(x_coords, y_coords, label="Line Group 2", color="orange")

    # Achsen anpassen
    plt.axhline(0, color='black',linewidth=0.5)
    plt.axvline(0, color='black',linewidth=0.5)
    plt.grid(color = 'gray', linestyle = '--', linewidth = 0.5)

    # Diagramm beschriften
    plt.title("Final Solution")
    plt.xlabel("X-Axis")
    plt.ylabel("Y-Axis")
    # Anzeige des Plots
    plt.show()


def plot_channel_polygon(t0, tn, ll, rr, choke_left, choke_right, left_channel, right_channel,
                         x_max, y_max, title, path=None):
    x_t0, y_t0 = zip(*t0)
    x_tn, y_tn = zip(*tn)
    x_ll, y_ll= zip(*ll)
    x_rr, y_rr = zip(*rr)

    all_left_posts = [t0[0], *[lp[0] for lp in left_channel], tn[0]]
    all_right_posts = [t0[1], *[rp[0] for rp in right_channel], tn[1]]
    x_left, y_left = zip(*all_left_posts)
    x_right, y_right = zip(*all_right_posts)

    fig = plt.figure(figsize=(7.0,7.0), dpi=100)

    left, bottom, width, height = (0.1, 0.1, 0.8, 0.75)
    ax = fig.add_axes((left, bottom, width, height))
    fig.suptitle(title)

    ax.set_xlim(left=None, right=x_max+10)
    ax.set_ylim(bottom=None, top=y_max+10)


    # plot both goals in black
    ax.plot(x_t0, y_t0, color='black')
    ax.plot(x_tn, y_tn, color='black')

    # plot ll in blue and rr in red and make them thinner (lw is line width)
    ax.plot(x_ll, y_ll, color='blue', lw=0.6)
    ax.plot(x_rr, y_rr, color='red', lw=0.6)

    # plot all left and right channels in the according color
    ax.plot(x_left, y_left, color='blue', lw=0.4, marker='x', mew=0.1)
    ax.plot(x_right, y_right, color="red", lw=0.4, marker='x', mew=0.1)

    # mark channel posts in according color
    #for channel_post in left_channel:
    #    ax.plot(*channel_post[0], color='blue', marker='x', mew=0.3)
    #for channel_post in right_channel:
    #    ax.plot(*channel_post[0], color="red", marker='x', mew=0.3)


    # plot choke points with a pop of a related color
    ax.plot(*choke_left[0], color='green', marker='o', mew=0.5)
    ax.plot(*choke_right[0], color='orange', marker='o', mew=0.5)

    if path is not None:
        path_lx, path_ly = zip(*path[1][0])
        if path[0][0]:
            l_color = 'blue'
        else:
            l_color = 'green'
        path_rx, path_ry = zip(*path[1][1])
        if path[0][1]:
            r_color = 'red'
        else:
            r_color = 'orange'
        ax.plot(path_lx, path_ly, color=l_color, lw=.4, marker='x')
        ax.plot(path_rx, path_ry, color=r_color, lw=.4, marker='x')

    plt.show()
