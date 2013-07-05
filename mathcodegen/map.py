from expression import Expression
from symbolic import symbolic
from helper import map_recursively
from mako.template import Template
import os

# mako template for generating c code
map_template = Template(
    filename=os.path.join(os.path.dirname(__file__), 'templates',
        'map.mako'))

def map(function, iterations=1, input=[], output=[], assignment='=',
    parallel=False):
    # evaluate indexing function for each array argument
    # and ensure access within array length
    def eval_indices(arg):
        if type(arg) in (list, tuple):
            index = arg[2] if len(arg) == 3 else lambda n, i, j: i
            name, length = arg[0], arg[1]

            index = index(Expression(length), Expression('i'), Expression('it'))
            index = '({i}>=0?{i}:0)'.format(i=index)
            index = '({i}<{l}?{i}:({l}-1))'.format(i=index, l=length)

            return name, length, index
        else:
            return arg

    input = map_recursively(eval_indices, input)
    output = map_recursively(eval_indices, output)

    # evaluate function symbolic and create result list if neccessary
    function_result = symbolic(function)(
        *['{}[{}]'.format(arg[0], arg[2]) if type(arg) in (tuple, list) else arg
            for arg in input])
    if type(function_result) not in (list, tuple):
        function_result = [function_result]

    # create code from mako template
    return map_template.render(
        input=input,
        output=output,
        result=[str(res) for res in function_result],
        dtype='float',
        iterations=iterations,
        assignment=assignment,
        parallel=parallel)