import os

from m2cgen import ast
from m2cgen.interpreters import mixins, utils
from m2cgen.interpreters.rust.code_generator import RustCodeGenerator
from m2cgen.interpreters.interpreter import ImperativeToCodeInterpreter


class RustInterpreter(ImperativeToCodeInterpreter,
                      mixins.LinearAlgebraMixin):

    supported_bin_vector_ops = {
        ast.BinNumOpType.ADD: "add_vectors",
    }

    supported_bin_vector_num_ops = {
        ast.BinNumOpType.MUL: "mul_vector_number",
    }

    abs_function_name = "f64::abs"
    atan_function_name = "f64::atan"
    exponent_function_name = "f64::exp"
    logarithm_function_name = "f64::ln"
    log1p_function_name = "f64::ln_1p"
    power_function_name = "f64::powf"
    sigmoid_function_name = "sigmoid"
    softmax_function_name = "softmax"
    sqrt_function_name = "f64::sqrt"
    tanh_function_name = "f64::tanh"

    with_sigmoid_expr = False
    with_softmax_expr = False

    def __init__(self, indent=4, function_name="score", *args, **kwargs):
        self.function_name = function_name

        cg = RustCodeGenerator(indent=indent)
        super().__init__(cg, *args, **kwargs)

    def interpret(self, expr):
        self._cg.reset_state()
        self._reset_reused_expr_cache()

        with self._cg.function_definition(
                name=self.function_name,
                args=[(True, self._feature_array_name)],
                is_scalar_output=expr.output_size == 1):
            last_result = self._do_interpret(expr)
            self._cg.add_return_statement(last_result)

        current_dir = os.path.dirname(__file__)

        if self.with_linear_algebra:
            filename = os.path.join(current_dir, "linear_algebra.rs")
            self._cg.add_code_lines(utils.get_file_content(filename))

        if self.with_softmax_expr:
            filename = os.path.join(current_dir, "softmax.rs")
            self._cg.add_code_lines(utils.get_file_content(filename))

        if self.with_sigmoid_expr:
            filename = os.path.join(current_dir, "sigmoid.rs")
            self._cg.add_code_lines(utils.get_file_content(filename))

        return self._cg.finalize_and_get_generated_code()

    def interpret_sigmoid_expr(self, expr, **kwargs):
        self.with_sigmoid_expr = True
        return super().interpret_sigmoid_expr(expr, **kwargs)

    def interpret_softmax_expr(self, expr, **kwargs):
        self.with_softmax_expr = True
        return super().interpret_softmax_expr(expr, **kwargs)