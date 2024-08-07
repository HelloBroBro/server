# Copyright 2024, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#  * Neither the name of NVIDIA CORPORATION nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import triton_python_backend_utils as pb_utils


class TritonPythonModel:
    def execute(self, requests):
        # Expect exactly one request per execute() call.
        if len(requests) != 1:
            pb_utils.Logger.log_error(f"Unexpected request length: {len(requests)}")
            raise Exception("Test FAILED")

        # Send a response with complete final flag, and then send another response and
        # and assert an exception is raised, for all requests.
        for request in requests:
            in_tensor = pb_utils.get_input_tensor_by_name(request, "INPUT0")
            out_tensor = pb_utils.Tensor("OUTPUT0", in_tensor.as_numpy())
            response = pb_utils.InferenceResponse([out_tensor])
            response_sender = request.get_response_sender()
            response_sender.send(
                response, flags=pb_utils.TRITONSERVER_RESPONSE_COMPLETE_FINAL
            )
            test_passed = False
            try:
                response_sender.send(response)
            except Exception as e:
                pb_utils.Logger.log_info(f"Raised exception: {e}")
                if (
                    str(e)
                    == "Unable to send response. Response sender has been closed."
                ):
                    test_passed = True
            finally:
                if not test_passed:
                    pb_utils.Logger.log_error("Expected exception not raised")
                    raise Exception("Test FAILED")
            pb_utils.Logger.log_info("Test Passed")
        return None
