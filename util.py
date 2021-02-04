#--------------------------------------------
#   Name: Tobi Ogunleye 
#   ID: 1636868
#   CMPUT 274, Fall 2020
#
#   Assignment 2: Huffman
#-------------------------------------------- 

from bitio import *
# chose to import all the functions, as the functions don't share names
# and it makes for cleaner looking code (I think)
from huffman import *
import pickle

def read_tree(tree_stream):
    '''Read a description of a Huffman tree from the given compressed
    tree stream, and use the pickle module to construct the tree object.
    Then, return the root node of the tree itself.

    Args:
      tree_stream: The compressed stream to read the tree from.

    Returns:
      A Huffman tree root constructed according to the given description.
    '''
    
    myTree = pickle.load(tree_stream)
    #could have been a one-liner, but did this for clarity
    return myTree

def decode_byte(tree, bitreader):
    """
    Reads bits from the bit reader and traverses the tree from
    the root to a leaf. Once a leaf is reached, bits are no longer read
    and the value of that leaf is returned.

    Args:
      bitreader: An instance of bitio.BitReader to read the tree from.
      tree: A Huffman tree.

    Returns:
      Next byte of the compressed bit stream.
    """
    try:
        #once we hit a tree, we can stop the recursion
        if isinstance(tree,TreeLeaf):
          return tree.getValue()
        bit = bitreader.readbit()
        #recursion block
        if bit == True: #if bit is a 1 go right, 0 go left
          return decode_byte(tree.getRight(),bitreader)
        elif bit == False:
          return decode_byte(tree.getLeft(),bitreader)
    except EOFError:
      pass #Just stop when we hit the EOF

def decompress(compressed, uncompressed):
    '''First, read a Huffman tree from the 'compressed' stream using your
    read_tree function. Then use that tree to decode the rest of the
    stream and write the resulting symbols to the 'uncompressed'
    stream.

    Args:
      compressed: A file stream from which compressed input is read.
      uncompressed: A writable file stream to which the uncompressed
          output is written.
    '''
    ntree = read_tree(compressed)
    nbitreader = BitReader(compressed)
    nbitwriter = BitWriter(uncompressed)
    endOfFile = False
    while not endOfFile:
      try:
        #the bit to be written
        wbit = decode_byte(ntree,nbitreader)
        if wbit != None:
    #Had a lot of trouble with writing this to uncompresed, found
    # a workaround on stack overflow: https://stackoverflow.com/questions/18367007/python-how-to-write-to-a-binary-file
    # Maybe I should have used writebit?
          nbitwriter.writebits(wbit,8)  
        else:
          endOfFile = True
      except EOFError:
        endOfFile = True

def write_tree(tree, tree_stream):
    '''Write the specified Huffman tree to the given tree_stream
    using pickle.

    Args:
      tree: A Huffman tree.
      tree_stream: The binary file to write the tree to.
    '''
    pickle.dump(tree,tree_stream)

def compress(tree, uncompressed, compressed):
    '''First write the given tree to the stream 'compressed' using the
    write_tree function. Then use the same tree to encode the data
    from the input stream 'uncompressed' and write it to 'compressed'.
    If there are any partially-written bytes remaining at the end,
    write 0 bits to form a complete byte.

    Flush the bitwriter after writing the entire compressed file.

    Args:
      tree: A Huffman tree.
      uncompressed: A file stream from which you can read the input.
      compressed: A file stream that will receive the tree description
          and the coded input data.
    '''
    ntree = write_tree(tree,compressed) 
    nbitwriter = BitWriter(compressed)
    #used this for reading as opposed to .read()
    compreader = BitReader(uncompressed)
    #create the dictionary first to make life easier 
    entable = make_encoding_table(tree)
    endOfFile = False

    while not endOfFile:
      try:
        #read 8 bits at a time
        rbit = compreader.readbits(8)
       # find the bit sequence of the byte we just read and write it
        for i in (entable[rbit]):
          if i == True:
            nbitwriter.writebit(1)
          else:
            nbitwriter.writebit(0)
      except EOFError:
        endOfFile = True
        #At the end of uncompressed, write None so the decompressor stops
        for x in entable[None]:
          if x == True:
            nbitwriter.writebit(1)
          else:
            nbitwriter.writebit(0)
        # Always flush when you're done writing   
        nbitwriter.flush()
    