
const loadMathJaxScript = (callback) => {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js';
    script.async = true;
    script.onload = callback;
    script.onerror = (error) => {
        console.error('MathJax script failed to load:', error);
    };
    document.body.appendChild(script);

    return () => {
        document.body.removeChild(script);
    };
};

const renderMath = (input, outputRef, displayStyle) => {
    if (!window.MathJax || !outputRef.current) {
        return;
    }

    window.MathJax.texReset();
    const options = {
        display: displayStyle
    };
    window.MathJax.tex2svgPromise(input, options).then((node) => {
        outputRef.current.innerHTML = '';
        outputRef.current.appendChild(node);
    }).catch((err) => {
        console.error('Error rendering MathJax:', err);
        outputRef.current.innerHTML = `<pre>Error: ${err.message}</pre>`;
    });
};

export { loadMathJaxScript, renderMath };
