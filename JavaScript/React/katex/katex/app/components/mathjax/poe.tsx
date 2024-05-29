'use client';
import React, { useState, useEffect } from 'react';
// import 'mathjax/es5/tex-svg.js';

const LatexToSvg = () => {
    const [input, setInput] = useState('%\n% Enter TeX commands below\n%\nx = {-b \\pm \\sqrt{b^2-4ac} \\over 2a}.');
    const [display, setDisplay] = useState(true);
    const [output, setOutput] = useState(null);
    const [isRendering, setIsRendering] = useState(false);

    // useEffect(() => {
    //     const convert = () => {
    //         setIsRendering(true);
    //         setOutput('');

    //         MathJax.texReset();
    //         const options = MathJax.getMetricsFor(document.getElementById('output'));
    //         options.display = display;

    //         MathJax.tex2svgPromise(input, options)
    //             .then(node => {
    //                 setOutput(node);
    //                 MathJax.startup.document.clear();
    //                 MathJax.startup.document.updateDocument();
    //             })
    //             .catch(err => {
    //                 setOutput(<pre>{err.message}</pre>);
    //             })
    //             .finally(() => {
    //                 setIsRendering(false);
    //             });
    //     };

    //     convert();
    // }, [input, display]);

    const handleInputChange = event => {
        setInput(event.target.value);
    };

    const handleDisplayChange = event => {
        setDisplay(event.target.checked);
    };

    const handleRender = () => {
        setInput(prevInput => prevInput.trim());
    };

    return (
        <div id="frame">
            <h1>MathJax v3: TeX to SVG</h1>
            <textarea
                id="input"
                rows="15"
                cols="10"
                value={input}
                onChange={handleInputChange}
            />
            <br />
            <div className="left">
                <input
                    type="checkbox"
                    id="display"
                    checked={display}
                    onChange={handleDisplayChange}
                />
                <label htmlFor="display">Display style</label>
            </div>
            <div className="right">
                <input
                    type="button"
                    value="Render TeX"
                    id="render"
                    onClick={handleRender}
                    disabled={isRendering}
                />
            </div>
            <br clear="all" />
            <div id="output">{output}</div>
        </div>
    );
};

export default LatexToSvg;