import React from 'react';
import { createRoot } from 'react-dom/client';

import 'katex/dist/katex.min.css';
import { BlockMath, InlineMath } from 'react-katex';

const ExamplePage = () => {
    const str1 = "首先，我们要理解题目中的两个算式的构成。观察第一个算式`\\frac{1}{2}+\\frac{7}{11}-\\frac{7}{11}`，可以看到有三个分数相加减。然后看第二个算式`\\frac{1}{2}+(\\frac{7}{11}-\\frac{7}{11})`，这里括号中有两个分数相减，外面还加上了一个分数。\n\n现在我们关注一下括号对算式的影响。在第一个算式中，没有任何括号，这意味着我们可以按照从左到右的顺序进行运算。而在第二个算式中，我们需要首先处理括号内的操作。\n\n那么，你认为括号中的`\\frac{7}{11}-\\frac{7}{11}`会得到什么结果呢"
    return (


        <div
            style={{
                width: '40%',
                margin: '0 auto',
            }}
        >
            <h1>
                <InlineMath>{'\\frac{n!}{k!(n-k)!} = \\binom{n}{k}'}</InlineMath>
            </h1>
            <h2>
                <code>{'<InlineMath />'}</code>
            </h2>
            This is an in-line expression <InlineMath math={'\\int_0^\\infty x^2 dx'} /> passed as <code>math prop</code>. This
            is an in-line <InlineMath math={'\\int_0^\\infty x^2 dx'} /> expression passed as <code>children prop</code>.
            <h2>
                <code>{'<BlockMath />'}</code>
            </h2>
            <BlockMath math={'\\int_0^\\infty x^2 dx'} />
            <BlockMath>{`A =
        \\begin{pmatrix}
        1 & 0 & 0 \\\\
        0 & 1 & 0 \\\\
        0 & 0 & 1 \\\\
        \\end{pmatrix}`}</BlockMath>
            <h2>Error handling</h2>
            <BlockMath math={'\\int_0^\\infty x^2 dx \\inta'} errorColor={'#cc0000'} />
            <BlockMath math="\\int_{" renderError={(err) => <b>Custom error message: {err.name}</b>} />
            <BlockMath math="\sum_{" />
            <BlockMath math={'\\sum_{'} renderError={(err) => <b>Custom error message: {err.name}</b>} />
            <BlockMath math={123} />
            <BlockMath math={123} renderError={(err) => <b>Custom error message: {err.name}</b>} />
        </div>)
};

export default ExamplePage;