import os
import tempfile
from huffman_tree import HuffmanTree
import numpy as np

# set marker value to separate different sections of compressed data
MARKER_VALUE = 255
# marker occurance defines the uniqueness of the marker. Higher
# marker occurance equals lower chance of input text mistaken as a marker
MARKER_OCCURANCE = 15
# creates marker with value repeated by occurance
MARKER_SEQUENCE = np.array([MARKER_VALUE]*MARKER_OCCURANCE, dtype=np.uint8)
# compressed file extension name
COMPRESSED_FILE_EXTENSION = ".huff"

class HuffFile:
    """
    This class provides methods for validating the file before compression
    or decompression, and for compressing and decompressing the file using 
    Huffman coding.
    """

    def __init__(self):
        pass


    # makes sure file is appropriate before compressing/decompressing
    def _validate_file(self, filename):
        # confirm filename is valid
        if not filename:
            raise ValueError("Error! File not declared properly.")
        # confirm file exists
        if not os.path.exists(filename):
            raise ValueError("Error! File does not exist.")
        # confirm file is readable
        if not os.access(filename, os.R_OK):
            raise ValueError("Error! File is not readable.")
        # confirm file is not empty
        if os.path.getsize(filename) == 0:
            raise ValueError("Error! File is empty.")


    def _is_text_file(self, filename):
        """
        Checks if a file is a text file.

        Args:
            filename (str): The name of the file to check.

        Returns:
            bool: True if the file is a text file, False otherwise.
        """

        # sample beginning of file to test for plain text
        sample = 1024
        try:
            with open(filename, "r") as file:
                file.read(sample)
        except UnicodeDecodeError:
            return False
        return True
    

    def _find_marker_sequence(self, data, marker_sequence):
        """
        This function finds the starting indices in the input file where
        the marker sequence begins

        Args:
            data (array): Data from the compressed file in which to find
            the marker sequence
            marker_sequence (array): Marker array that contains MARKER_VALUE
            as elements and size MARKER_OCCURANCE

        Returns:
            list: A list of starting indices of each marker array
        """
        marker_length = len(marker_sequence)
        return [i for i in range(len(data) - marker_length + 1) 
            if np.array_equal(data[i:i+marker_length], marker_sequence)]


    def compress_file(self, filename):
        """
        Compresses a file to contain binary code, serial code, and file length
        needed for decompression.

        The binary code is a string of 0s and 1s generated by the compress 
        function in huffman_tree.py. The serial code are the instructions for 
        recreating the Huffman tree, also obtained from the compress function 
        in huffman_tree.py.

        Args:
            filename (str): The name of the file being compressed.

        Returns:
            new_dir (str): The absolute location of the compressed file
        """
        
        # validate if file exists, is readable, and is not empty
        try:
            self._validate_file(filename)

            # validate if file is of the right type
            if not self._is_text_file(filename):
                raise ValueError("Error! File is not a plain text file.")
        except ValueError as e:
            raise CompressionError(str(e))
        
        # open file and read input data
        with open(filename, "r") as file:
            input_data = file.read()

        # obtain bit_string and serial_code from compress function
        ht = HuffmanTree()
        bit_string, serial_code = ht.compress(input_data)

        # pack bit_string
        code_bit_array = np.array(list(map(int, bit_string)))
        pack_code_data = np.packbits(code_bit_array)

        # get length of bit string and pack into 64-bit chunk
        bit_length = np.array([len(bit_string)], dtype=np.uint64)
        bit_len_bytes = np.frombuffer(bit_length.tobytes(), dtype=np.uint8)

        # convert serial code to bytes using UTF-8 encoding
        serial_code_bytes = serial_code.encode('utf-8')
        # convert each byte to binary string then join strings together
        serial_data_bin = ''.join(format(byte, '08b') 
                                  for byte in serial_code_bytes)
        # pack serial_code
        serial_data_bit_array = np.array(list(map(int, serial_data_bin)))
        pack_serial_data = np.packbits(serial_data_bit_array)

        # concatenate bit_string, length of bit_string, and serial_code
        # separated by markers to compressed_data
        compressed_data = np.concatenate([pack_code_data, MARKER_SEQUENCE, 
                                          bit_len_bytes, MARKER_SEQUENCE,
                                          pack_serial_data, MARKER_SEQUENCE])
        
        # create new unique directory for the compressed file to be placed in
        curr_dir = os.path.dirname(filename) # path to current directory of the file being compressed
        temp_dir = tempfile.TemporaryDirectory(dir=curr_dir)
        new_dir = os.path.basename(temp_dir.name) # get the unique name for directory
        temp_dir.cleanup() # remove the temp directory
        new_dir = os.path.join(curr_dir, new_dir) # path to new directory
        os.mkdir(new_dir) # make the new directory

        # write compressed data to a new file with specified file extension
        compressed_data.tofile(new_dir + "\\" + os.path.basename(filename) + 
                               COMPRESSED_FILE_EXTENSION)

        # return the location of compressed file as a string
        return new_dir


    def decompress_file(self, filename):
        """
        This function decompresses a given file with COMPRESSED_FILE_EXTENSION

        Args: 
            filename (str): The name of the file to decompress

        Returns:
            str: The name of the decompressed file 
        """

        try:
            self._validate_file(filename)
            # confirm file is of correct extension
            original_filename, file_extension = os.path.splitext(filename)
            if file_extension != COMPRESSED_FILE_EXTENSION:
                raise ValueError("Error! File is not of type" + 
                                COMPRESSED_FILE_EXTENSION)
        except ValueError as e:
            raise CompressionError(str(e))
        
        # open file and read compressed data
        # read binary file
        read_data = np.fromfile(filename, dtype=np.uint8)

        # array that contains starting indices of MARKER_SEQUENCE in read_data
        marker_location = self._find_marker_sequence(read_data, MARKER_SEQUENCE)

        # extract packed data, length, and serial data from compressed file
        packed_data = read_data[:marker_location[0]]
        length_data = read_data[marker_location[0] + 
                                MARKER_OCCURANCE:marker_location[1]]
        serial_data = read_data[marker_location[1] + 
                                MARKER_OCCURANCE:marker_location[2]]

        # unpack data (bit_string) into numpy array of bits
        unpacked_data = np.unpackbits(packed_data)
        # retrieve original length data of bit_string from file
        original_length = np.frombuffer(length_data, dtype=np.uint64)[0]
        # convert the unpacked data (up to original length) into string
        unpacked_data_str = ''.join(map(str, unpacked_data[:original_length]))

        # unpack data (serial_code) into numpy array of bits
        unpacked_serial_data = np.unpackbits(serial_data)
        # convert unpacked serial data back to string
        unpacked_serial_data_str = ''.join(map(str, unpacked_serial_data))
        # split serial data string into 8-bit chunks
        unpacked_serial_data_chunks = [unpacked_serial_data_str[i:i+8] for i in 
                                       range(0, len(unpacked_serial_data_str), 8)]
        # for each 8-bit chunk to bytes
        unpacked_serial_data_bytes = bytes(int(chunk, 2) for chunk 
                                           in unpacked_serial_data_chunks)
        # decode bytes back into a string using UTF-8 decoding
        serial_data_str = unpacked_serial_data_bytes.decode('utf-8')
        
        # create instance of huffman tree to call decompression
        ht = HuffmanTree()
        decompressed_data = ht.decompress(unpacked_data_str, serial_data_str)
        # write to compressed file the decompressed string
        # decompress file
        with open(filename, 'w') as f:
            f.write(decompressed_data)

        # return to original filename
        os.rename(filename, original_filename)

# identify class to raise exceptions from other files
class CompressionError(Exception):
    pass