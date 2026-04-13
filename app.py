import ast
import base64
import io

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from flask import Flask, render_template, request

app = Flask(__name__)

ALLOWED_NAMES = {
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "arcsin": np.arcsin,
    "arccos": np.arccos,
    "arctan": np.arctan,
    "sinh": np.sinh,
    "cosh": np.cosh,
    "tanh": np.tanh,
    "exp": np.exp,
    "log": np.log,
    "log10": np.log10,
    "sqrt": np.sqrt,
    "abs": np.abs,
    "pi": np.pi,
    "e": np.e,
}


class SafeExprChecker(ast.NodeVisitor):
    ALLOWED_NODES = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.Mod,
        ast.USub,
        ast.UAdd,
        ast.Call,
        ast.Name,
        ast.Load,
        ast.Constant,
    )

    def visit(self, node):
        if not isinstance(node, self.ALLOWED_NODES):
            raise ValueError(f"許可されていない構文です: {type(node).__name__}")
        return super().visit(node)

    def visit_Call(self, node):
        if not isinstance(node.func, ast.Name):
            raise ValueError("関数呼び出し形式が不正です")
        if node.func.id not in ALLOWED_NAMES:
            raise ValueError(f"許可されていない関数です: {node.func.id}")
        for arg in node.args:
            self.visit(arg)

    def visit_Name(self, node):
        if node.id != "x" and node.id not in ALLOWED_NAMES:
            raise ValueError(f"許可されていない名前です: {node.id}")


def compile_expr(expr: str):
    tree = ast.parse(expr, mode="eval")
    SafeExprChecker().visit(tree)
    code = compile(tree, "<expr>", "eval")

    def f(x):
        env = {"x": x, **ALLOWED_NAMES}
        return eval(code, {"__builtins__": {}}, env)

    return f


def generate_plot(exprs, xmin, xmax, points, title):
    x = np.linspace(xmin, xmax, points)
    fig, ax = plt.subplots(figsize=(9, 5.5))

    plotted = 0
    warnings = []
    for expr in exprs:
        try:
            func = compile_expr(expr)
            y = func(x)
            ax.plot(x, y, label=f"y = {expr}")
            plotted += 1
        except Exception as exc:
            warnings.append(f"'{expr}' は描画できません: {exc}")

    if plotted == 0:
        raise ValueError("描画できる式がありません。式を見直してください。")

    ax.axhline(0, color="black", linewidth=0.8)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(title)
    ax.legend()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)

    image_data = base64.b64encode(buf.read()).decode("utf-8")
    return image_data, warnings


@app.route('/', methods=['GET', 'POST'])
def index():
    form = {
        'expr': 'x**2, sin(x)',
        'xmin': '-10',
        'xmax': '10',
        'points': '1000',
        'title': 'Function Graph',
    }
    image_data = None
    error = None
    warnings = []

    if request.method == 'POST':
        form['expr'] = request.form.get('expr', '').strip()
        form['xmin'] = request.form.get('xmin', '-10').strip()
        form['xmax'] = request.form.get('xmax', '10').strip()
        form['points'] = request.form.get('points', '1000').strip()
        form['title'] = request.form.get('title', 'Function Graph').strip() or 'Function Graph'

        try:
            exprs = [e.strip() for e in form['expr'].split(',') if e.strip()]
            if not exprs:
                raise ValueError('式を1つ以上入力してください。')

            xmin = float(form['xmin'])
            xmax = float(form['xmax'])
            points = int(form['points'])

            if xmin >= xmax:
                raise ValueError('xmin は xmax より小さくしてください。')
            if points < 2:
                raise ValueError('points は 2 以上にしてください。')

            image_data, warnings = generate_plot(exprs, xmin, xmax, points, form['title'])
        except Exception as exc:
            error = str(exc)

    return render_template('index.html', form=form, image_data=image_data, error=error, warnings=warnings)


if __name__ == '__main__':
    app.run(debug=True)
