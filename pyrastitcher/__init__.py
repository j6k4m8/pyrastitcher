import uuid
import subprocess
import os
import sys


version = "0.0.1"

_valid_refs = ['x', 'y', 'z', '-x', '-y', '-z']

class Pyrastitcher:

    def __init__(self, **kwargs):
        """
        Generates a new Pyrastitcher class. Generally, you can just run this
        with no arguments, but if you need to specify the path of the binary,
        then pass in `terastitcher_path`.
        """
        self.path = os.path.expanduser(
            kwargs.get('terastitcher_path', 'terastitcher')
        )

        self._verbose = kwargs.get('verbose', False)

        self._last_xml = ""
        self._tmp_files = []

    def _output(self, output):
        if self._verbose:
            sys.stderr.write(output)

    def _clean_up_files(self):
        for f in self._tmp_files:
            self._delete_tmpfile(f)

    def _delete_tmpfile(self, f):
        if f in self._tmp_files:
            self._tmp_files.remove(f)
            os.remove(f)

    def _generate_tempfile(self):
        f = os.path.expanduser(
            "~/pyrastitcher-" + str(uuid.uuid4()) + ".xml"
        )
        self._tmp_files.append(f)
        return f

    def import_folders(self, volin, refs, voxel_size, **kwargs):
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

        # Verify that volin is valid
        if not (os.path.isdir(volin) and os.path.exists(volin)):
            raise ValueError("volin {} is not a valid directory.".format(volin))

        # Generate a random filename in which to store the XML output from
        # Terastitcher. Can't use tempfiles for some reason...
        # TODO: Why can't we use tempfiles?
        tempfile_name = self._generate_tempfile()

        # We sanitize refs by lower-casing.
        refs = [r.lower() for r in refs]
        if len(refs) != 3 or sum([refs[d] in _valid_refs for d in range(3)]) != 3:
            raise ValueError("'refs' argument must be an iterable of length 3 " +
                             "of values in {x, y, z, -x, -y, -z}.")

        # Now we sanitize voxel_size by coercing to floats:
        voxel_size = [float(v) for v in voxel_size]

        # Now we can run the import.
        output = subprocess.check_output([
            self.path,
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
        self._last_xml = xml

        # Clean up after ourselves.
        self._delete_tmpfile(tempfile_name)
        self._output(output)
        return xml


    def _simple_in_out(self, cmd, xml=None, **kwargs):
        # TODO: kwargs. There's more than zero of them.

        if xml is None:
            xml = self._last_xml

        tmpf_in = self._generate_tempfile()
        with open(tmpf_in, 'w+b') as tfni:
            tfni.write(xml)

        tmpf_out = self._generate_tempfile()
        output = subprocess.check_output([
            self.path,
            cmd,
            '--projin={}'.format(tmpf_in),
            '--projout={}'.format(tmpf_out)
        ])

        xmlf = open(tmpf_out, 'rb')
        xmlf.seek(0)
        xml = xmlf.read()

        self._last_xml = xml

        self._delete_tmpfile(tmpf_in)
        self._delete_tmpfile(tmpf_out)
        self._output(output)
        return xml

    def align(self, xml=None, **kwargs):
        """
        Runs the alignment algorithm (--displcompute).

        Arguments:
            xml (str): The XML descriptor (generally, it came from an above import)

        Returns:
            str: The XML projout.
        """
        # TODO: kwargs. There's more than zero of them.

        return self._simple_in_out('--displcompute', xml)

    def project(self, xml=None, **kwargs):
        """
        Runs the project algorithm (--displproj).

        Arguments:
            xml (str): The XML descriptor (generally, it came from an above import)

        Returns:
            str: The XML projout.
        """
        # TODO: kwargs. There's more than zero of them.

        return self._simple_in_out('--displproj', xml)

    def threshold(self, threshold, xml=None, **kwargs):
        """
        Evaluate the displacement reliabilities ('--displthres'), based on a
        threshold between 0 and 1.

        Arguments:
            xml (str): The XML descriptor (generally, it came from an above import)
            threshold (float): The threshold for confidence between 0 and 1.

        Returns:
            str: The XML projout.
        """
        # TODO: kwargs. There's more than zero of them.

        if xml is None:
            xml = self._last_xml

        if threshold > 1 or threshold < 0:
            raise ValueError("Argument 'threshold' must be between 0 and 1.")

        tmpf_in = self._generate_tempfile()
        with open(tmpf_in, 'w+b') as tfni:
            tfni.write(xml)

        tmpf_out = self._generate_tempfile()
        output = subprocess.check_output([
            self.path,
            '--displthres',
            '--projin={}'.format(tmpf_in),
            '--threshold={}'.format(threshold),
            '--projout={}'.format(tmpf_out)
        ])

        xmlf = open(tmpf_out, 'rb')
        xmlf.seek(0)
        xml = xmlf.read()

        self._last_xml = xml

        self._delete_tmpfile(tmpf_in)
        self._delete_tmpfile(tmpf_out)
        self._output(output)
        return xml

    def place(self, xml=None, **kwargs):
        """
        Places the tiles according to the (--placetiles) protocol.

        Arguments:
            xml (str): The XML descriptor (generally, it came from an above import)

        Returns:
            str: The XML projout.
        """
        # TODO: kwargs. There's more than zero of them.

        return self._simple_in_out('--placetiles', xml)

    def merge(self, volout, xml=None, **kwargs):
        """
        Perform the actual merge. The default returns a series of 2D, full
        scale tiff files. Future releases will permit multires and 3D.

        Arguments:
            volout (str): A path to the vol-out.

        Returns:
            boolean: True on success.
        """
        # TODO: kwargs. There's more than zero of them.

        if xml is None:
            xml = self._last_xml

        tmpf_in = self._generate_tempfile()
        with open(tmpf_in, 'w+b') as tfni:
            tfni.write(xml)

        output = subprocess.check_output([
            self.path,
            '--merge',
            '--projin={}'.format(tmpf_in),
            '--volout={}'.format(volout)
        ])

        self._delete_tmpfile(tmpf_in)
        self._output(output)
        return True

    def run(self, volin, refs, voxel_size, threshold, volout):
        pass
