id = ''


def gen_id(id1, id2):
    """
    Dash pages require each component in the app to have a totally
    unique id for callbacks. This is easy for small apps, but harder for larger
    apps where there is overlapping functionality on each page.
    For example, each page might have a div that acts as a trigger for reloading;
    instead of typing "page1-trigger" every time, this function allows you to
    just use id('trigger') on every page.

    How:
        prepends the page to every id passed to it
    Why:
        saves some typing and lowers mental effort
    **Example**
    """

    return str(id1) + "_" + str(id2)


def init_id(id_init):
    return id_init
