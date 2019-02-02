# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Tests for lite.py functionality related to select TF op usage."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tensorflow.lite.python import lite
from tensorflow.lite.python.interpreter import Interpreter
from tensorflow.python.client import session
from tensorflow.python.framework import dtypes
from tensorflow.python.framework import test_util
from tensorflow.python.ops import array_ops
from tensorflow.python.platform import test


@test_util.run_v1_only('b/120545219')
class FromSessionTest(test_util.TensorFlowTestCase):

  def testFlexMode(self):
    in_tensor = array_ops.placeholder(
        shape=[1, 16, 16, 3], dtype=dtypes.float32)
    out_tensor = in_tensor + in_tensor
    sess = session.Session()

    # Convert model and ensure model is not None.
    converter = lite.TFLiteConverter.from_session(sess, [in_tensor],
                                                  [out_tensor])
    converter.target_ops = set([lite.OpsSet.SELECT_TF_OPS])
    tflite_model = converter.convert()
    self.assertTrue(tflite_model)

    # Ensures the model contains TensorFlow ops.
    # TODO(nupurgarg): Check values once there is a Python delegate interface.
    interpreter = Interpreter(model_content=tflite_model)
    with self.assertRaises(RuntimeError) as error:
      interpreter.allocate_tensors()
    self.assertIn(
        'Regular TensorFlow ops are not supported by this interpreter. Make '
        'sure you invoke the Flex delegate before inference.',
        str(error.exception))


if __name__ == '__main__':
  test.main()