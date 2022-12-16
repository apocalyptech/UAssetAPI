#!/usr/local/dv/virtualenv/pythonnet/bin/python3
# vim: set expandtab tabstop=4 shiftwidth=4:

# Copyright 2022 Christopher J Kucera
# <cj@apocalyptech.com>
# <https://apocalyptech.com/contact.php>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import sys
import json
import argparse
import subprocess


class Statement:

    shape_margins = {
            'larrow': '0.15,0.15',
            'rarrow': '0.15,0.15',
            'rpromoter': '0.15,0.15',
            'cds': '0.11,0.15',
            }

    def __init__(self, data, level=0):
        self.data = data
        self.level = level
        self.prefix = '    '*self.level
        self.type = data['Inst']
        if 'StatementIndex' in data:
            self.index = data['StatementIndex']
            self.dot_name = f's{self.index}'
        else:
            self.index = None
            self.dot_name = None

        # The following really don't make sense for nested
        # expressions, but whatever.
        self.link_to_next = True
        self.next = None
        self.shape = 'box'
        self.color = 'black'
        self.fillcolor = 'white'
        self.styles = ['filled']

    def inline_label(self):
        return self.type

    def _dot_label(self):
        return [f'{self.prefix}{self.inline_label()}']

    def dot_label(self):
        lines = []
        lines.append('&lt;{}&gt; <b>{}</b>'.format(
            self.index,
            self.type,
            ))
        lines.extend(self._dot_label())
        # Need a final <br> at the end so the last line is left-justified
        lines.append('')
        return '<br align="left"/>'.join(lines)

    def dot_node(self):
        margin = '0.11,0.055'
        if self.shape in self.shape_margins:
            margin = self.shape_margins[self.shape]
        return '{} [label=<{}> shape={} color={} fillcolor={} style="{}" margin="{}"];'.format(
                self.dot_name,
                self.dot_label(),
                self.shape,
                self.color,
                self.fillcolor,
                ','.join(self.styles),
                margin,
                )

    def _dot_links(self):
        return []

    def dot_links(self):
        links = []
        if self.link_to_next and self.next:
            links.append(f'{self.dot_name} -> {self.next.dot_name} [weight=2];')
        for link in self._dot_links():
            if type(link) == tuple:
                link_num, link_attrs = link
                dest = f's{link_num} [{link_attrs}]'
            else:
                dest = f's{link}'
            links.append(f'{self.dot_name} -> {dest};')
        return links

    @staticmethod
    def from_data(statement, level=0):
        global statement_types
        statement_type = statement['Inst']
        if statement_type in statement_types:
            return statement_types[statement_type](statement, level)
        else:
            print(f'NOTICE: Unknown statement type: {statement_type}')
            return Statement(statement, level)


class _HardValue(Statement):

    def __init__(self, data, value, level=0):
        super().__init__(data, level)
        self.value = value

    def inline_label(self):
        return self.value


class NoObject(_HardValue):

    def __init__(self, data, level=0):
        super().__init__(data, 'None', level)


class Nothing(_HardValue):

    def __init__(self, data, level=0):
        super().__init__(data, 'Nothing', level)


class Self(_HardValue):

    def __init__(self, data, level=0):
        super().__init__(data, 'Self', level)


class DeprecatedOp4A(_HardValue):

    def __init__(self, data, level=0):
        super().__init__(data, '(deprecated op 4A)', level)
        print('NOTE: DeprecatedOp4A is currently untested.  Verify and make sure this works!')


class NoInterface(_HardValue):

    def __init__(self, data, level=0):
        super().__init__(data, 'NoInterface', level)
        print('NOTE: NoInterface is currently untested.  Verify and make sure this works!')


class Breakpoint(_HardValue):

    def __init__(self, data, level=0):
        super().__init__(data, '(Breakpoint)', level)
        print('NOTE: Breakpoint is currently untested.  Verify and make sure this works!')


class WireTracepoint(_HardValue):

    def __init__(self, data, level=0):
        super().__init__(data, '(WireTracepoint)', level)
        print('NOTE: WireTracepoint is currently untested.  Verify and make sure this works!')


class Tracepoint(_HardValue):

    def __init__(self, data, level=0):
        super().__init__(data, '(Tracepoint)', level)
        print('NOTE: Tracepoint is currently untested.  Verify and make sure this works!')


class _IndexHardValue(Statement):

    def __init__(self, data, value, level=0):
        super().__init__(data, level)
        self.value = value
        self.index = data['_hotfix_index']

    def inline_label(self):
        return f'[{self.index}] {self.value}'


class STrue(_IndexHardValue):

    def __init__(self, data, level=0):
        super().__init__(data, 'True', level)


class SFalse(_IndexHardValue):

    def __init__(self, data, level=0):
        super().__init__(data, 'False', level)


class IntZero(_IndexHardValue):

    def __init__(self, data, level=0):
        super().__init__(data, 0, level)
        print('NOTE: IntZero is currently untested.  Verify and make sure this works!')


class IntOne(_IndexHardValue):

    def __init__(self, data, level=0):
        super().__init__(data, 1, level)
        print('NOTE: IntOne is currently untested.  Verify and make sure this works!')


class _Const(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.value = data['Value']

    def inline_label(self):
        return self.value


class SkipOffsetConst(_Const):
    """
    No changes we care about
    """


class StringConst(_Const):
    """
    No changes we care about
    """


class UnicodeStringConst(_Const):
    """
    No changes we care about (apart from the note about being untested)
    """

    def __init__(self, data, level=0):
        super().__init__(data, level)
        print('NOTE: UnicodeStringConst is currently untested.  Verify and make sure this works!')


class _IndexConst(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.index = data['_hotfix_index']
        self.value = data['Value']

    def inline_label(self):
        return f'[{self.index}] {self.value}'


class ByteConst(_IndexConst):
    """
    No changes we care about
    """


class IntConst(_IndexConst):
    """
    No changes we care about
    """


class IntConstByte(_IndexConst):
    """
    No changes we care about
    """

    def __init__(self, data, level=0):
        super().__init__(data, level)
        print('NOTE: IntConstByte is currently untested.  Verify and make sure this works!')


class Int64Const(_IndexConst):
    """
    No changes we care about
    """

    def __init__(self, data, level=0):
        super().__init__(data, level)
        print('NOTE: Int64Const is currently untested.  Verify and make sure this works!')


class UInt64Const(_IndexConst):
    """
    No changes we care about
    """

    def __init__(self, data, level=0):
        super().__init__(data, level)
        print('NOTE: UInt64Const is currently untested.  Verify and make sure this works!')


class FloatConst(_IndexConst):
    """
    No changes we care about
    """


class NameConst(_IndexConst):
    """
    No changes we care about
    """


class TextConst(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.text_type = data['TextLiteralType']
        if self.text_type == 'Empty':
            self.value = ''
        elif self.text_type == 'LocalizedText':
            self.value = data['SourceString']
            self.loc_key = data['LocalizationKey']
            self.loc_namespace = data['LocalizationNamespace']
        elif self.text_type == 'InvariantText':
            print('NOTE: TextConst of type InvariantText is currently untested.  Verify and make sure this works!')
            self.value = data['SourceString']
        elif self.text_type == 'LiteralString':
            print('NOTE: TextConst of type LiteralString is currently untested.  Verify and make sure this works!')
            self.value = data['SourceString']
        elif self.text_type == 'StringTableEntry':
            print('NOTE: TextConst of type StringTableEntry is currently untested.  Verify and make sure this works!')
            self.table_id = data['TableId']
            self.table_key = data['TableKey']
            self.value = f'{self.table_id}[{self.table_key}]'
        else:
            print('WARNING: Unknown TextConst type found')
            self.value = '(APOC - UNKNOWN)'

    def inline_label(self):
        return self.value


class ObjectConst(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.index = data['_hotfix_index']
        self.object = data['Object']
        if '.' in self.object:
            self.object = self.object.rsplit('.', 1)[0]

    def inline_label(self):
        return f'[{self.index}] {self.object}'


class FieldPathConst(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        print('NOTE: FieldPathConst is currently untested.  Verify and make sure this works!')
        self.expression = Statement.from_data(data['Expression'], level)

    def inline_label(self):
        return self.expression.inline_label()


class RotationConst(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.index = data['_hotfix_index']
        self.pitch = data['Pitch']
        self.yaw = data['Yaw']
        self.roll = data['Roll']

    def inline_label(self):
        return f'[{self.index}] ({self.pitch}, {self.yaw}, {self.roll})'


class VectorConst(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.index = data['_hotfix_index']
        self.x = data['X']
        self.y = data['Y']
        self.z = data['Z']

    def inline_label(self):
        return f'[{self.index}] ({self.x}, {self.y}, {self.z})'


class TransformConst(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        print('NOTE: TransformConst is currently untested.  Verify and make sure this works!')
        self.index = data['_hotfix_index']
        self.rot_x = data['Rotation']['X']
        self.rot_y = data['Rotation']['Y']
        self.rot_z = data['Rotation']['Z']
        self.rot_w = data['Rotation']['W']
        self.trans_x = data['Translation']['X']
        self.trans_y = data['Translation']['Y']
        self.trans_z = data['Translation']['Z']
        self.scale_x = data['Scale']['X']
        self.scale_y = data['Scale']['Y']
        self.scale_z = data['Scale']['Z']

    def inline_label(self):
        return ' '.join([
            f'[{self.index}]',
            f'rot:({self.rot_x},{self.rot_y},{self.rot_z},{self.rot_w})',
            f'trans:({self.trans_x},{self.trans_y},{self.trans_z})',
            f'scale:({self.scale_x},{self.scale_y},{self.scale_z})',
            ])


class ArrayConst(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.outer = data['Variable Outer']
        self.values = []
        for value in data['Values']:
            self.values.append(Statement.from_data(value, level+2))

    def _dot_label(self):
        lines = []
        lines.append(f'{self.prefix}Array {self.outer}:')
        for idx, value in enumerate(self.values):
            lines.append(f'{self.prefix}{idx})')
            lines.extend(value._dot_label())
        return lines


class SoftObjectConst(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.value = Statement.from_data(data['Value'], level)

    def inline_label(self):
        return self.value.inline_label()


class SetArray(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.left = Statement.from_data(data['LeftSideExpression'])
        self.values = []
        for value in data['Values']:
            self.values.append(Statement.from_data(value, level+2))

    def _dot_label(self):
        lines = []
        lines.append(f'{self.prefix}{self.left.inline_label()} =')
        for idx, value in enumerate(self.values):
            lines.append(f'{self.prefix}{idx})')
            lines.extend(value._dot_label())
        return lines


class Context(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.context = Statement.from_data(data['Context'], level)
        self.expression = Statement.from_data(data['Expression'], level)

    def _dot_label(self):
        lines = []
        # On second thought, reporting on this doesn't seem too useful
        #lines.append(f'{self.prefix}(ctx: {self.context.inline_label()})')
        lines.extend(self.expression._dot_label())
        return lines

    def inline_label(self):
        return self.expression.inline_label()


class InterfaceContext(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.expression = Statement.from_data(data['Expression'], level)

    def _dot_label(self):
        lines = []
        lines.extend(self.expression._dot_label())
        return lines

    def inline_label(self):
        return self.expression.inline_label()


class Let(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.shape = 'ellipse'
        self.var = Statement.from_data(data['Variable'], level+1)
        self.val = Statement.from_data(data['Expression'], level+1)

    def _dot_label(self):
        lines = []
        lines.append(f'{self.prefix}{self.var.inline_label()} = ')
        lines.extend(self.val._dot_label())
        return lines


class LetBool(Let):
    """
    No changes that we care about
    """


class LetObj(Let):
    """
    No changes that we care about
    """


class LetDelegate(Let):
    """
    No changes that we care about
    """


class LetWeakObjPtr(Let):
    """
    No changes that we care about
    """


class LetMulticastDelegate(Let):
    """
    No changes that we care about (apart from the non-tested note)
    """

    def __init__(self, data, level=0):
        super().__init__(data, level)
        print('NOTE: LetMulticastDelegate is currently untested.  Verify and make sure this works!')


class Function(Statement):

    def __init__(self, data, level=0, func_key='Function'):
        super().__init__(data, level)
        self.func_key = func_key
        self.function = data[func_key]
        self.parameters = []
        self.shape = 'cds'
        self.fillcolor = 'gold1'
        for param in data['Parameters']:
            self.parameters.append(Statement.from_data(param, level+1))

    def _dot_label(self):
        lines = []
        lines.append(f'{self.prefix}{self.type} {self.function} (')
        for param in self.parameters:
            lines.append(f'{self.prefix}  {param.inline_label()},')
        lines.append(f'{self.prefix})')
        return lines


class FinalFunction(Function):
    """
    No changes we care about
    """


class VirtualFunction(Function):
    """
    No changes we care about
    """


class LocalVirtualFunction(Function):

    def __init__(self, data, level=0):
        super().__init__(data, level, func_key='FunctionName')
        print('NOTE: LocalVirtualFunction is currently untested.  Verify and make sure this works!')


class LocalFinalFunction(Function):
    """
    No changes we care about (apart from the alert about not being tested)
    """

    def __init__(self, data, level=0):
        super().__init__(data, level)
        print('NOTE: LocalFinalFunction is currently untested.  Verify and make sure this works!')


class CallMath(Function):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.contextclass = data['ContextClass']


class _Variable(Statement):
    """
    TODO: The initial examples of this that I'd run into all pointed "into" the
    same object as the ubergraph, and so it seemed reasonable to truncate
    the display (for both inline labels and dot labels) to just the final variable
    bit.  I've now run into at least one instance where it's calling outside,
    though, so we may want to consider reporting on the full var name.  Maybe
    have an optional arg passed into these things containing the current object
    name, and strip if it matches?  Anyway, the example of external references
    can be found in: /Game/Maps/Zone_3/MotorcadeInterior/MotorcadeInterior_Plot,
    specifically in the RemoveMulticastDelegate at index 20156.
    """

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.name = data['Variable Name']
        self.outer = data['Variable Outer']
        self.shape = 'ellipse'
        if '.' in self.name:
            self.name = self.name.split('.', 1)[-1]

    def inline_label(self):
        return self.name


class LocalVariable(_Variable):
    """
    No changes we care about
    """


class LocalOutVariable(_Variable):
    """
    No changes we care about
    """


class InstanceVariable(_Variable):
    """
    No changes we care about
    """


class DefaultVariable(LocalVariable):
    """
    No changes we care about (apart from the non-tested note)
    """

    def __init__(self, data, level=0):
        super().__init__(data, level)
        print('NOTE: DefaultVariable is currently untested.  Verify and make sure this works!')


class Jump(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.shape = 'rarrow'
        self.fillcolor = 'aquamarine'
        self.offset = data['Offset']
        self.link_to_next = False

    def _dot_label(self):
        lines = []
        lines.append(f'-&gt; {self.offset}')
        return lines

    def _dot_links(self):
        return [self.offset]


class JumpIfNot(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.shape = 'rarrow'
        self.fillcolor = 'aquamarine2'
        self.offset = data['Offset']
        self.condition = Statement.from_data(data['Condition'], level)

    def _dot_label(self):
        lines = []
        lines.extend(self.condition._dot_label())
        lines.append(f'-&gt; {self.offset}')
        return lines

    def _dot_links(self):
        return [(self.offset, 'label=<Not> color=red fontcolor=red')]


class ComputedJump(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.shape = 'rpromoter'
        self.fillcolor = 'aquamarine2'
        self.styles.append('dashed')
        self.offset = Statement.from_data(data['OffsetExpression'], level)
        self.link_to_next = False

    def _dot_label(self):
        lines = []
        lines.append(f'[{self.index}] -&gt; {self.offset.inline_label()}')
        return lines


class PushExecutionFlow(Statement):
    """
    Actually have no idea how exactly the Push/Pop execution flow stuff works.
    It seems to me like it might be sort of a gosub?  In which case maybe
    we *do* still want to link_to_next?
    """

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.shape = 'rarrow'
        self.fillcolor = 'deepskyblue1'
        self.offset = data['Offset']
        #self.link_to_next = False

    def _dot_label(self):
        lines = []
        lines.append(f'-&gt; {self.offset}')
        return lines

    def _dot_links(self):
        return [(self.offset, 'label=<PushFlow> color=blue fontcolor=blue')]


class PopExecutionFlow(Statement):
    """
    Actually have no idea how exactly the Push/Pop execution flow stuff works.
    It seems to me like it might be sort of a gosub?  In which case maybe
    we *do* still want to link_to_next?
    """

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.shape = 'larrow'
        self.fillcolor = 'chartreuse3'
        self.link_to_next = False


class PopExecutionFlowIfNot(Statement):
    """
    Actually have no idea how exactly the Push/Pop execution flow stuff works.
    It seems to me like it might be sort of a gosub?  In which case maybe
    we *do* still want to link_to_next?
    """

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.shape = 'larrow'
        self.fillcolor = 'chartreuse3'
        self.condition = Statement.from_data(data['Condition'], level)

    def _dot_label(self):
        lines = []
        lines.extend(self.condition._dot_label())
        return lines


class StructMemberContext(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.name = data['Property Name']
        self.expression = Statement.from_data(data['StructExpression'], level+1)

    def _dot_label(self):
        lines = []
        lines.append(f'{self.prefix}{self.name} of:')
        lines.extend(self.expression._dot_label())
        return lines

    def inline_label(self):
        return self.name


class Return(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.shape = 'larrow'
        self.fillcolor = 'chartreuse2'
        self.expression = Statement.from_data(data['Expression'], level)

    def _dot_label(self):
        lines = []
        lines.append(f'{self.prefix}{self.expression.inline_label()}')
        return lines


class EndOfScript(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.shape = 'octagon'
        self.fillcolor = 'indianred1'
        self.link_to_next = False

    def _dot_label(self):
        return []


class BindDelegate(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        # TODO: read in Function too?
        self.delegate = Statement.from_data(data['Delegate'], level)
        self.object = Statement.from_data(data['Object'], level)

    def _dot_label(self):
        lines = []
        lines.append(f'{self.prefix}{self.delegate.inline_label()} to:')
        lines.append(f'{self.prefix}    {self.object.inline_label()}')
        return lines


class DynamicCast(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.to_class = data['Class']
        self.expression = Statement.from_data(data['Expression'], level)

    def _dot_label(self):
        lines = []
        lines.append(f'{self.prefix}(Cast {self.expression.inline_label()} as')
        lines.append(f'{self.prefix}    {self.to_class})')
        return lines


class PrimitiveCast(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.cast_type = data['CastType']
        self.expression = Statement.from_data(data['Expression'], level)

    def _dot_label(self):
        lines = []
        lines.append(f'{self.prefix}(Cast {self.expression.inline_label()} via')
        lines.append(f'{self.prefix}    {self.cast_type})')
        return lines


class ObjToInterfaceCast(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.to_class = data['InterfaceClass']
        self.expression = Statement.from_data(data['Expression'], level)

    def _dot_label(self):
        lines = []
        lines.append(f'{self.prefix}(Cast {self.expression.inline_label()} as')
        lines.append(f'{self.prefix}    {self.to_class})')
        return lines


class CrossInterfaceCast(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        print('NOTE: CrossInterfaceCast is currently untested.  Verify and make sure this works!')
        self.to_class = data['InterfaceClass']
        self.expression = Statement.from_data(data['Expression'], level)

    def _dot_label(self):
        lines = []
        lines.append(f'{self.prefix}(Cast {self.expression.inline_label()} as')
        lines.append(f'{self.prefix}    {self.to_class})')
        return lines


class InterfaceToObjCast(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        print('NOTE: InterfaceToObjCast is currently untested.  Verify and make sure this works!')
        self.to_class = data['ObjectClass']
        self.expression = Statement.from_data(data['Expression'], level)

    def _dot_label(self):
        lines = []
        lines.append(f'{self.prefix}(Cast {self.expression.inline_label()} as')
        lines.append(f'{self.prefix}    {self.to_class})')
        return lines


class SwitchCase:

    def __init__(self, key, value):
        self.key = key
        self.value = value


class SwitchValue(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.expression = Statement.from_data(data['Expression'], level)
        self.cases = []
        for option in data['Cases']:
            self.cases.append(SwitchCase(
                Statement.from_data(option['CaseValue'], level+1),
                Statement.from_data(option['CaseResult'], level+2),
                ))
        self.default = Statement.from_data(data['DefaultResult'], level+2)

    def _dot_label(self):
        lines = []
        lines.append(f'{self.prefix}Switch {self.expression.inline_label()}:')
        for option in self.cases:
            #lines.append(f'{self.prefix}    {option.key.inline_label()}: {option.value.inline_label()}')
            lines.append(f'{self.prefix}    {option.key.inline_label()}:')
            lines.extend(option.value._dot_label())
        #lines.append(f'{self.prefix}    (default): {self.default.inline_label()}')
        lines.append(f'{self.prefix}    (default):')
        lines.extend(self.default._dot_label())
        return lines


class StructConst(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.struct = data['Struct']
        if '_interpreted_guid' in data:
            self.guid = data['_interpreted_guid']
        else:
            self.guid = None
        self.properties = {}
        for key, vals in data['Properties'].items():
            self.properties[key] = []
            for val in vals:
                self.properties[key].append(Statement.from_data(val, level+2))

    def inline_label(self):
        bits = []
        for key, vals in self.properties.items():
            for val in vals:
                bits.append(str(val.inline_label()))
        if self.guid is None:
            return 'StructConst({})'.format(','.join(bits))
        else:
            return 'StructConst({} (guid: {}))'.format(','.join(bits), self.guid)

    def _dot_label(self):
        lines = []
        lines.append(f'{self.prefix}Struct:')
        if self.guid is not None:
            lines.append(f'{self.prefix}    (guid: {self.guid})')
        for key, vals in self.properties.items():
            lines.append(f'{self.prefix}    {key}:')
            for val in vals:
                lines.extend(val._dot_label())
        return lines


class LetValueOnPersistentFrame(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.outer = data['Property Outer']
        self.name = data['Property Name']
        if '.' in self.name:
            self.name = self.name.split('.', 1)[-1]
        self.expression = Statement.from_data(data['Expression'], level+1)

    def _dot_label(self):
        lines = []
        lines.append(f'{self.prefix}{self.name} =')
        lines.extend(self.expression._dot_label())
        return lines

    def inline_label(self):
        return self.name


class AddMulticastDelegate(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.multicast = Statement.from_data(data['MulticastDelegate'], level+1)
        self.delegate = Statement.from_data(data['Delegate'], level+1)

    def _dot_label(self):
        lines = []
        lines.append(f'{self.prefix}MulticastDelegate:')
        lines.extend(self.multicast._dot_label())
        lines.append(f'{self.prefix}Delegate:')
        lines.extend(self.delegate._dot_label())
        return lines


class RemoveMulticastDelegate(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.multicast = Statement.from_data(data['MulticastDelegate'], level+1)
        self.delegate = Statement.from_data(data['Delegate'], level+1)

    def _dot_label(self):
        lines = []
        lines.append(f'{self.prefix}MulticastDelegate:')
        lines.extend(self.multicast._dot_label())
        lines.append(f'{self.prefix}Delegate:')
        lines.extend(self.delegate._dot_label())
        return lines


class ClearMulticastDelegate(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        print('NOTE: ClearMulticastDelegate is currently untested.  Verify and make sure this works!')
        self.multicast = Statement.from_data(data['MulticastDelegate'], level)

    def _dot_label(self):
        return self.multicast._dot_label()


class CallMulticastDelegate(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.self_context = data['DelegateSignatureFunction']['IsSelfContext']
        self.function_parent = data['DelegateSignatureFunction']['MemberParent']
        self.function_name = data['DelegateSignatureFunction']['MemberName']
        self.delegate = Statement.from_data(data['Delegate'], level+1)
        self.parameters = []
        if len(data['Parameters']) > 0:
            print('NOTE: Parameters inside CallMulticastDelegate are currently untested.  Verify and make sure this works!')
        for param in data['Parameters']:
            self.parameters.append(Statement.from_data(param, level+1))

    def _dot_label(self):
        lines = []
        lines.append(f'{self.prefix}{self.delegate.inline_label()} -&gt;')
        lines.append(f'{self.prefix}{self.function_parent} (')
        for param in self.parameters:
            lines.append(f'{self.prefix}  {param.inline_label()},')
        lines.append(f'{self.prefix})')
        return lines


class MetaCast(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.class_name = data['Class']
        self.expression = Statement.from_data(data['Expression'], level+1)

    def inline_label(self):
        return f'({self.class_name}) {self.expression.inline_label()}'


class ArrayGetByRef(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        self.array = Statement.from_data(data['ArrayExpression'], level+1)
        self.index = Statement.from_data(data['IndexExpression'], level+1)

    def inline_label(self):
        return f'{self.array.inline_label()}[{self.index.inline_label()}]'


class InstanceDelegate(Statement):

    def __init__(self, data, level=0):
        super().__init__(data, level)
        print('NOTE: InstanceDelegate is currently untested.  Verify and make sure this works!')
        self.index = data['_hotfix_index']
        self.function = data['FunctionName']

    def inline_label(self):
        return f'[{self.index}] {self.function}'


statement_types = {
        'AddMulticastDelegate': AddMulticastDelegate,
        'ArrayConst': ArrayConst,
        'ArrayGetByRef': ArrayGetByRef,
        'BindDelegate': BindDelegate,
        'Breakpoint': Breakpoint,
        'ByteConst': ByteConst,
        'CallMath': CallMath,
        'CallMulticastDelegate': CallMulticastDelegate,
        'ClearMulticastDelegate': ClearMulticastDelegate,
        'ComputedJump': ComputedJump,
        'Context': Context,
        'CrossInterfaceCast': CrossInterfaceCast,
        'DefaultVariable': DefaultVariable,
        'DeprecatedOp4A': DeprecatedOp4A,
        'DynamicCast': DynamicCast,
        'EndOfScript': EndOfScript,
        'False': SFalse,
        'FieldPathConst': FieldPathConst,
        'FinalFunction': FinalFunction,
        'FloatConst': FloatConst,
        'InstanceDelegate': InstanceDelegate,
        'InstanceVariable': InstanceVariable,
        'Int64Const': Int64Const,
        'IntConst': IntConst,
        'IntConstByte': IntConstByte,
        'InterfaceContext': InterfaceContext,
        'InterfaceToObjCast': InterfaceToObjCast,
        'IntOne': IntOne,
        'IntZero': IntZero,
        'Jump': Jump,
        'JumpIfNot': JumpIfNot,
        'Let': Let,
        'LetBool': LetBool,
        'LetDelegate': LetDelegate,
        'LetMulticastDelegate': LetMulticastDelegate,
        'LetObj': LetObj,
        'LetValueOnPersistentFrame': LetValueOnPersistentFrame,
        'LetWeakObjPtr': LetWeakObjPtr,
        'LocalFinalFunction': LocalFinalFunction,
        'LocalOutVariable': LocalOutVariable,
        'LocalVariable': LocalVariable,
        'LocalVirtualFunction': LocalVirtualFunction,
        'MetaCast': MetaCast,
        'NameConst': NameConst,
        'NoInterface': NoInterface,
        'NoObject': NoObject,
        'Nothing': Nothing,
        'ObjectConst': ObjectConst,
        'ObjToInterfaceCast': ObjToInterfaceCast,
        'PopExecutionFlow': PopExecutionFlow,
        'PopExecutionFlowIfNot': PopExecutionFlowIfNot,
        'PrimitiveCast': PrimitiveCast,
        'PushExecutionFlow': PushExecutionFlow,
        'RemoveMulticastDelegate': RemoveMulticastDelegate,
        'Return': Return,
        'RotationConst': RotationConst,
        'Self': Self,
        'SetArray': SetArray,
        'SkipOffsetConst': SkipOffsetConst,
        'SoftObjectConst': SoftObjectConst,
        'StringConst': StringConst,
        'StructConst': StructConst,
        'StructMemberContext': StructMemberContext,
        'SwitchValue': SwitchValue,
        'TextConst': TextConst,
        'Tracepoint': Tracepoint,
        'TransformConst': TransformConst,
        'True': STrue,
        'UInt64Const': UInt64Const,
        'UnicodeStringConst': UnicodeStringConst,
        'VectorConst': VectorConst,
        'VirtualFunction': VirtualFunction,
        'WireTracepoint': WireTracepoint,

        # Bytecode that we're not handling smartly yet, mostly just because
        # they looked a bit complex and I hadn't run across any live examples
        # of them to confirm.  They'll still show up in the graphs, of course,
        # just without any extra info.
        #'SetSet': SetSet,
        #'SetConst': SetConst,
        #'SetMap': SetMap,
        #'MapConst': MapConst,
        #'Assert': Assert,
        #'InstrumentationEvent': InstrumentationEvent,
        }

class Script:

    def __init__(self, filename):
        self.filename = filename
        with open(filename) as df:
            data = json.load(df)
        self.statements = []
        for statement in data:
            parsed = Statement.from_data(statement)
            if len(self.statements) > 0:
                self.statements[-1].next = parsed
            self.statements.append(parsed)

    def to_dotfile(self, filename):
        with open(filename, 'w') as df:
            print('digraph ubergraph {', file=df)
            print('', file=df)
            print('// Nodes', file=df)
            for statement in self.statements:
                print(statement.dot_node(), file=df)
            print('', file=df)
            print('// Links', file=df)
            for statement in self.statements:
                for link in statement.dot_links():
                    print(link, file=df)
            print('', file=df)
            print('}', file=df)

def main():

    parser = argparse.ArgumentParser(
            description='Represent Ubergraph bytecode scripts as dotfiles',
            )

    # NOTE: Depending on viewing application, SVG output doesn't always
    # do our text-alignment stuff properly
    parser.add_argument('-r', '--render',
            choices=['png', 'svg', 'none'],
            default='svg',
            help='Render type',
            )

    parser.add_argument('-d', '--display',
            type=str,
            default='feh',
            help='Application to use to display renders',
            )

    parser.add_argument('--no-display',
            action='store_false',
            dest='do_display',
            help="Don't auto-display renders",
            )

    parser.add_argument('filename',
            nargs=1,
            help='JSON filename to process',
            )

    args = parser.parse_args()
    filename = args.filename[0]
    if filename.endswith('.'):
        filename += 'json'
    filename_base = filename.rsplit('.', 1)[0]
    if filename_base == filename:
        filename += '.json'
    filename_dot = f'{filename_base}.dot'
    filename_render = f'{filename_base}.{args.render}'

    # Load and convert to dot
    script = Script(filename)
    script.to_dotfile(filename_dot)
    print(f'Generated: {filename_dot}')

    # Render
    if args.render != 'none':

        # Remove the render if it already exists
        if os.path.exists(filename_render):
            os.unlink(filename_render)

        # Render it!
        subprocess.run(['dot', f'-T{args.render}', '-o', filename_render, filename_dot])

        # Check to make sure that worked
        if os.path.exists(filename_render):
            print(f'Rendered to: {filename_render}')
            if args.render in {'png', 'svg'} and args.do_display:
                subprocess.run([args.display, filename_render])
        else:
            print(f'WARNING: Could not render to: {filename_render}')

if __name__ == '__main__':
    main()

