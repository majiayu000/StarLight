'use client';
import 'katex/dist/katex.min.css';
import React, { useEffect, useRef } from 'react';
import katex from 'katex';

function MathComponent({ formula }) {
    const mathElement = useRef(null);

    useEffect(() => {
        console.log("formula", { formula })
        if (mathElement.current) {
            katex.render(formula, mathElement.current, {
                "displayMode": true, "leqno": false, "fleqn": false, "throwOnError": false, "errorColor": "#cc0000", "strict": "warn", "output": "htmlAndMathml", "trust": false, "macros": { "\\f": "#1f(#2)" }
            });

            katex.render(String.raw`c = \pm\sqrt{a^2 + b^2}`, mathElement.current, {
                throwOnError: false
            });
        }
    }, [formula]);

    return <span ref={mathElement} />;
}

export default MathComponent;