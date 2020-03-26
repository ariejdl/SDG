
# jupyter-client >= 6.0

import jupyter_client

from jupyter_client import kernelspec

print(kernelspec.find_kernel_specs())

from jupyter_client.asynchronous import AsyncKernelClient
from jupyter_client.manager import start_new_kernel, start_new_async_kernel
from jupyter_client.multikernelmanager import AsyncMultiKernelManager

# can then follow this https://github.com/jupyter/jupyter_client/issues/358
# km, kc = start_new_kernel(kernel_name='python3')
#km, kc = start_new_kernel(kernel_name='julia-1.2')

mkm = AsyncMultiKernelManager()

kid1 = await mkm.start_kernel(kernel_name='python3')
kid2 = await mkm.start_kernel(kernel_name='julia-1.2')

# mkm.interrupt...
# etc.

km = mkm.get_kernel(kid1)
kc = km.client()

# see tests for KernelManager

# see tests for KernelClient
# https://github.com/jupyter/jupyter_client/blob/master/jupyter_client/tests/test_client.py
# start_channels()
# stop_channels()

print(kc.iopub_channel)

# info:
# mkm.list_kernel_ids()
# mkm.get_kernel(kid)
# km.kernel_name
