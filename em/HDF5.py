# here, trace["id"] = index in HDF5
# unless using special Numpy array created using np.empty, it is ok to let h5py allocate the array for us w/ classic slicing
# no need to use *_direct methods
# retrieve parent and friends using get() rather than [] (returns None vs. raises exception)
# TODO
# make the traces dataset resizable by doing maxshape=(None, trace_len) in create_dataset - so that I can add traces later on (but trace_len - dim 1 - is fixed and cannot be changed) -- does this preserve existing traces?
# use region references stored in the h5 file to define the various train/test splits for the various analysis/attack campaigns (instead of having multiple files with the same traces, I only have one -- more efficient)
# name of regions comes from master CFG (see book on how to name a region)
# labels for a given train campaign are computed at the beginning of said campaign by a function which takes all the metadata available in the file and filters it (path to .py which contains corresponding function in master CFG)
# TODO SWMR to be able to perform analyses (here, create trace delta file to send on compute machine) as the traces are being acquired in order to know when to stop the acquisitions

import atexit
import h5py
import hdf5plugin
import numpy as np

__MODULE_NAME = 'storage'
__MODULE_STATIC_CODE = {'check_no_data': __is_empty_observations_h5}

__FILENAME = 'traces.h5'
__MAX_TRACES = 1000000

MIN_BATCH_SIZE = 100

# TODOIMM module for simple plot of trace in HDF5 (this is an analysis?)

# TODO this is no longer about traces/metadata -> data/metadata

# TODO move FILENAME to CFG file ('filename' key in storage module)
# TODO new format (following new file structure: observations.h5, analyses.h5, attacks.h5)
# file.h5 -> subcampaign_name_1 (Group) -> data (Dataset)
#                                       -> metadata (Dataset)
#        ....                          ....
#         -> subcampaign_name_n         -> data (Dataset)
#                                       -> metadata (Dataset)
# NOTE: it is possible to create new groups/datasets in an existing HDF5 file. use 'r+' when opening - I have a guarantee that file already exists (even if this is the first campaign, everything has already been created by experiment_manager.py)
# TODO analyses get {data,metadata} format from h5 file by using dataset.dtype.descr (much easier than reading it from sections in CFG file which would involve custom code/loading of modules - might not be possible. This works because I expect a given analysis module to work on one group only (possibly comprising multiple datasets such as data,metadata)
# TODO acquisitions get dtype from module description in CFG file (data_format,metadata_format keys in "params"), then callback_chain in probe related breakpoints merge those pieces of information in local_storage (dict used in the chain) so that last module in chain can store everything properly. 

def __trim_storage():
    f = h5py.File(__traces_path, 'a')

    f['metadata'].resize((__traces_count,))
    f['data'].resize((__traces_count, __trace_length))

    f.close()

def __is_empty_observations_h5(): # TODOIMM becomes observations.h5[subcampaign_key (timing, EM, ...)] = not empty
    # I check observations.h5 only since, if the user performed an anlysis/attack, it has to rely on observations. Hence observations.h5 is not empty. Moreover, they may have only acquired observations but not analyzed them yet, in which case, observations.h5 is not empty as well.

# TODOIMM trace length no longer specified in CFG file, use data_dtype
def init_module(campaign_storage, module_info):
    global __batch_size, __compress_metadata, __conversion_required, __dtype
    global __trace_dtype_in, __trace_dtype_out, __trace_length, __traces_path
    global __traces, __traces_count

    utils = campaign_storage['utils_module']

    params = utils.get_module_params(__MODULE_NAME, campaign_storage)
    for name, key in params.items():
        exec(f'global __{name}; __{name} = campaign_storage["{key}"]')

    # TODO [MIN/MAX]_BATCH_SIZE should be computed from __trace_length and trace_dtype_size (MIN -> based on write speed - min 1s of write [that is write_speed/(__trace_length*trace_dtype_size)], MAX -> max RAM for this module divided by size of a single trace). If writing this buffer takes too long, use threads for this purpose (described in DSO90404A.py)
    if __batch_size < MIN_BATCH_SIZE:
        __batch_size = MIN_BATCH_SIZE

    # TODOLATER use utils.get_keys_from_path (the one which allows wildcards) to determine whether a probe (the only possible source of data) has been loaded (pkl.py as well)
    if not 'probe_trace_dtype' in campaign_storage@@: # TODO is this disjunction really necessary (acquisition and profiling should be the same code with different params from CFG file)
        __trace_dtype_in = __dtype_out
        __trace_dtype_out = __dtype_in
        __conversion_required = __trace_dtype_in != __trace_dtype_out

        # TODO (global) do not rely on campaign_type (OK w/ new get_keys_from_path using '*')
        __traces_path = campaign_storage[utils.get_key_from_path(
            campaign_storage['campaign_type']@@, 'campaign_path'
        )] + __FILENAME
    else: # I am doing an acquisition campaign
        __trace_dtype_in = campaign_storage['probe_trace_dtype']
        __trace_dtype_out = __dtype_out
        __conversion_required = __trace_dtype_in != __trace_dtype_out

        data_dtype = campaign_storage[utils.get_key_from_path(
            campaign_storage['campaign_type']@@, 'data_dtype'
        )] this is no longer from CFG file, but computed from callback chain (caveat: must simulate callback chain once during init)
        metadata_dtype = campaign_storage[utils.get_key_from_path(
            campaign_storage['campaign_type']@@, 'metadata_dtype'
        )]
        dt = [
            ('metadata', metadata_dtype.descr),
            ('data', data_dtype.descr)
        ]
        __traces = np.zeros(__batch_size, dtype=dt)
        __traces_count = 0

        __traces_path = campaign_storage[utils.get_key_from_path(
            campaign_storage['campaign_type']@@, 'campaign_path'
        )] + __FILENAME
        # I use a fixed libver to make sure that all objects
        # in the file use some reasonably recent features of
        # the HDF5 format (I am setting the lower bound of 
        # libver)
        # TODO use 'a' in case the user wants to add more traces
        # to an existing campaign
        # in this case, count existing traces to determine where to resume in the existing pairs file or if I have to look for a new one
        f = h5py.File(
            __traces_path, 'w', libver='v112', fs_strategy="fsm", fs_persist=True
        )

        # TODO this should become 'cfg_b64_gzip' and be stored once per group rather than at file level in case config changes between subcampaigns contained in a single observations.h5 file
        f.attrs['cfg_name'] = campaign_storage[utils.get_key_from_path(
            'general', 'name'
        )]

        if __compress_metadata:
            f.create_dataset(
                'metadata', (__MAX_TRACES,), metadata_dtype,
                maxshape=(None,), **hdf5plugin.Blosc(
                    cname='zstd', clevel=1,
                    shuffle=hdf5plugin.Blosc.BITSHUFFLE
                ), fletcher32=True
            )
        else:
            f.create_dataset(
                'metadata', (__MAX_TRACES,), metadata_dtype,
                maxshape=(None,), fletcher32=True
            )

	# TODO doc says chunks are laid out 'haphazardly' in the file. Choose chunks based on estimated average read speed during analyses -> read analyses machine names from CFG file, and bench them at CFG file creation time, then let experiments_manager suggest min (1s read) chunk and max (max RAM usage) size on console so that user can put their own (one of these or another) in the CFG file. Read_size for analyses must be a multiple of chunk size
	# TODO => get chunks parameter from CFG file
	# no need to use the chunk cache since I read exactly once (I don't work on the h5py.File object) the data (n chunk[s], n >= 1) for all possible analyses, and then work on the resulting numpy object
        f.create_dataset(
            'data', (__MAX_TRACES, __trace_length), 
            __trace_dtype_out, chunks=(1, __trace_length),
            maxshape=(None, __trace_length), 
            **hdf5plugin.Blosc(
                cname='zstd', clevel=1,
                shuffle=hdf5plugin.Blosc.BITSHUFFLE
            ),
            fletcher32=True
        )

        f.close()

        # when the acquisitions are done (i.e when the top script exits), I resize the dataset to its true size
        atexit.register(__trim_storage)
        atexit.regiter(save_trace)

def list_traces():
    f = h5py.File(__traces_path, 'r')
    count = f['data'].shape[0]
    f.close()

    return np.arange(count, dtype='int32')

def read_metadata(ids_array):
    ids_array = np.sort(ids_array, kind='heapsort')

    f = h5py.File(__traces_path, 'r')
    metadata_array = f['metadata'][ids_array]
    f.close()

    new_dtype = metadata_array.dtype.descr + [('id', 'int32')]
    metadata_id_array = np.zeros(metadata_array.shape, dtype=new_dtype)

    for field in metadata_array.dtype.descr:
        metadata_id_array[field[0]] = metadata_array[field[0]]
    metadata_id_array['id'] = ids_array

    return metadata_id_array

def read_traces(metadata_array):
    metadata_array = np.sort(metadata_array, kind='heapsort', order='id')

    f = h5py.File(__traces_path, 'r')
    traces_array = f['data'][metadata_array['id']]
    f.close()

    if __conversion_required:
        traces_array = traces_array.astype(__trace_dtype_out)

    return traces_array

def save_preamble(preamble):
    f = h5py.File(__traces_path, 'a')
    f.attrs['preamble'] = preamble
    f.close()

def __write_traces():
    f = h5py.File(__traces_path, 'a')

    f['metadata'][__write_traces.current_index:__traces_count] = __traces['metadata']
    f['data'][__write_traces.current_index:__traces_count] = __traces['data']

    f.close()

    __write_traces.current_index = __traces_count
__write_traces.current_index = 0

def save_trace(metadata=None, trace=None):
    global __traces, __traces_count

    if not (metadata is None):
        # TODO this has been superseded by new {data/metadata}_format keys
        trace = np.frombuffer(trace, dtype=__trace_dtype_in)
        if __conversion_required:
            trace = trace.astype(__trace_dtype_out)

        idx = __traces_count % __batch_size

        __traces[idx]['metadata'] = metadata
        __traces[idx]['data'] = trace
        __traces_count += 1

        if __traces_count % __batch_size == 0:
            __write_traces()
    else: # I am flushing out the buffer
        __write_traces()
