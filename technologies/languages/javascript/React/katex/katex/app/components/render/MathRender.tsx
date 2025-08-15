import React, { useEffect, useRef } from 'react';
import katex from 'katex';

const MathRenderer = ({ math, inline = false }) => {
    useEffect(() => {
        if (typeof window !== 'undefined') {
            const elements = document.getElementsByClassName('math-render');
            for (const element of elements) {
                katex.render(element.textContent, element, {
                    throwOnError: false,
                    displayMode: !inline,
                });
            }
        }
    }, [math, inline]);

    return <span className="math-render">{math}</span>;
};


const KaTeXComponent = ({ texExpression }) => {
    const containerRef = useRef();

    useEffect(() => {
        katex.render(texExpression, containerRef.current);
    }, [texExpression]);

    return <div ref={containerRef} />
}

export default KaTeXComponent;
