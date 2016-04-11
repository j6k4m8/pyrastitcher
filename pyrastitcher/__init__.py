import uuid
import subprocess
import os
import sys


version = "0.0.1"

_valid_refs = ['x', 'y', 'z', '-x', '-y', '-z']


def _generate_tempfile():
    return os.path.expanduser(
        "~/pyrastitcher-" + str(uuid.uuid4()) + ".xml"
    )


def import_folders(volin, refs, voxel_size, **kwargs):
    """
    Imports into Terastitcher using the "Import from two-level heirarchy of
    folders" protocol from the documentation.

    Arguments:
        volin (str): The path to the root directory of files.
        refs (int[3] : ('x', 'y', 'z')): The reference system.
        voxel_size (float[3] : (1, 1, 1)): The voxel size, in microns.
        volin_plugin (str : "TiledXY|2Dseries"): The plugin to use
        imin_plugin (str : "tiff2D"): The imin plugin to use

    Returns:
        (str, str): (output, XML)
    """

    terastitcher = os.path.expanduser(
        kwargs.get('terastitcher_path', 'terastitcher')
    )

    # Verify that volin is valid
    if not (os.path.isdir(volin) and os.path.exists(volin)):
        raise ValueError("volin {} is not a valid directory.".format(volin))

    # Generate a random filename in which to store the XML output from
    # Terastitcher. Can't use tempfiles for some reason...
    # TODO: Why can't we use tempfiles?
    tempfile_name = _generate_tempfile()

    # We sanitize refs by lower-casing.
    refs = [r.lower() for r in refs]
    if len(refs) != 3 or sum([refs[d] in _valid_refs for d in range(3)]) != 3:
        raise ValueError("'refs' argument must be an iterable of length 3 " +
                         "of values in {x, y, z, -x, -y, -z}.")

    # Now we sanitize voxel_size by coercing to floats:
    voxel_size = [float(v) for v in voxel_size]

    # Now we can run the import.
    output = subprocess.check_output([
        terastitcher,
        '--import',
        '--volin={}'.format(volin),
        '--ref1={}'.format(refs[0]),
        '--ref2={}'.format(refs[1]),
        '--ref3={}'.format(refs[2]),
        '--vxl1={}'.format(voxel_size[0]),
        '--vxl2={}'.format(voxel_size[1]),
        '--vxl3={}'.format(voxel_size[2]),
        '--projout={}'.format(tempfile_name)
    ])

    xmlf = open(tempfile_name, 'rb')
    xmlf.seek(0)
    xml = xmlf.read()

    # Clean up after ourselves.
    os.remove(tempfile_name)
    sys.stderr.write(output)
    return xml


def align(xml, **kwargs):
    """
    Runs the alignment algorithm (--displcompute).

    Arguments:
        xml (str): The XML descriptor (generally, it came from an above import)

    Returns:
        str: The XML projout.
    """

    # TODO: kwargs. There's more than zero of them. (e.g. subvoldim)

    terastitcher = os.path.expanduser(
        kwargs.get('terastitcher_path', 'terastitcher')
    )

    tmpf_in = _generate_tempfile()
    with open(tmpf_in, 'w+b') as tfni:
        tfni.write(xml)

    tmpf_out = _generate_tempfile()

    output = subprocess.check_output([
        terastitcher,
        '--displcompute',
        '--projin="{}"'.format(tmpf_in),
        '--projout={}'.format(tmpf_out)
    ])

    xmlf = open(tmpf_out, 'rb')
    xmlf.seek(0)
    xml = xmlf.read()

    os.remove(tmpf_in)
    os.remove(tmpf_out)
    sys.stderr.write(output)
    return xml
