#!/usr/bin/env python

from __future__ import print_function
import sys, os, subprocess, re, logging
import pysam

def make_directory(inputDir):
    """
    make input directory if it does not exist.
    """
    if inputDir != '' and not os.path.exists(inputDir):
        os.makedirs(inputDir)


def make_parent_directory(inputFile):
    """
    make the parent directory of the inputFile if it does not exist
    """
    absInputFile = os.path.abspath(inputFile)
    parentDir_absInputFile = os.path.dirname(absInputFile)
    make_directory(parentDir_absInputFile)


def compress_index_bed(inputFile, outputFile):

    ####################
    # compress by bgzip
    hOUT = open(outputFile, "w")
    subprocess.call(["bgzip", "-f", "-c", inputFile], stdout = hOUT)
    hOUT.close()
    ####################

    ####################
    # index by tabix
    subprocess.call(["tabix", "-p", "bed", outputFile])
    ####################


def sortBedpe(inputFile, outputFile, sort_option):

    hOUT = open(outputFile, "w")
    subprocess.call(["sort", "-k1,1", "-k2,2n", "-k4,4", "-k5,5n"] + sort_option.split(" ") + [inputFile], stdout = hOUT)
    hOUT.close()


def processingMessage(message):

    FORMAT = '%(asctime)s: %(message)s'
    logging.basicConfig(format=FORMAT, datefmt='%m/%d/%Y %H:%M:%S', level = logging.INFO)
    logger = logging.getLogger('genomonSV_log')
    logger.info(message)


def warningMessage(message):

    # logger = logging.getLogger('genomonSV_log')
    # logger.warning(message)
    print(message, file = sys.stderr)


def get_seq(reference, chr, start, end):

    seq = ""
    for item in pysam.faidx(reference, chr + ":" + str(start) + "-" + str(end)):
        # if item[0] == ">": continue
        seq = seq + item.rstrip('\n')
    seq = seq.replace('>', '')
    seq = seq.replace(chr + ":" + str(start) + "-" + str(end), '')

    if re.search(r'[^ACGTUWSMKRYBDHVNacgtuwsmkrybdhvn]', seq) is not None:
        print("The return value in get_seq function includes non-nucleotide characters:", file = sys.stderr)
        print(seq, file = sys.stderr)
        sys.exit(1)

    return seq



def reverseComplement(seq):
    complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A',
                  'W': 'W', 'S': 'S', 'M': 'K', 'K': 'M', 'R': 'Y', 'Y': 'R',
                  'B': 'V', 'V': 'B', 'D': 'H', 'H': 'D', 'N': 'N'}

    return("".join(complement.get(base, base) for base in reversed(seq)))

def getPysamSamfile(inputBAM, reference_genome):
    bamfile = ""
    seq_filename, seq_ext = os.path.splitext(inputBAM)
    if seq_ext == ".cram":
        if os.path.isfile(reference_genome):
            bamfile = pysam.AlignmentFile(inputBAM, "rc", reference_filename=reference_genome)
        else:
            # bamfile = pysam.AlignmentFile(inputBAM, "rc")
            print("Please enter the reference genome, when reading the cram file.")
            sys.exit(1)
    else:
        bamfile = pysam.AlignmentFile(inputBAM, "rb")
    return bamfile


