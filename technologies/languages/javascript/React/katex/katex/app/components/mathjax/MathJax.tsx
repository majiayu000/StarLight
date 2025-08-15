'use client';
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { loadMathJaxScript, renderMath } from './MathJaxLoader'; // adjust the path as necessary

const MathJaxRenderer = () => {
	const [input, setInput] = useState('x = {-b \\pm \\sqrt{b^2-4ac} \\over 2a}');
	const [displayStyle, setDisplayStyle] = useState(true);
	const outputRef = useRef(null);

	const removeScriptRef = useRef(null);

	const loadMathJaxScriptCached = useCallback(loadMathJaxScript, []);
	const renderMathCached = useCallback(renderMath, []);

	useEffect(() => {
		const removeScript = loadMathJaxScriptCached(() => renderMathCached(input, outputRef, displayStyle));
		return removeScript;
	}, [input, displayStyle, loadMathJaxScriptCached, renderMathCached]);

	useEffect(() => {
		return removeScriptRef.current || (() => { });
	}, []);
	return (
		<div style={{ maxWidth: '40em', margin: 'auto' }}>
			<h1>MathJax v3: TeX to SVG</h1>
			<textarea
				rows="15"
				cols="10"
				value={input}
				onChange={e => setInput(e.target.value)}
				style={{ width: '100%', fontSize: '120%', border: '1px solid grey', boxSizing: 'border-box' }}
			/>
			<br />
			<div style={{ float: 'left' }}>
				<input
					type="checkbox"
					checked={displayStyle}
					onChange={() => setDisplayStyle(!displayStyle)}
				/> <label>Display style</label>
			</div>
			<div style={{ float: 'right' }}>
				<input type="button" value="Render TeX" onClick={() => renderMath(input, outputRef, displayStyle)} />
			</div>
			<br style={{ clear: 'both' }} />
			<div ref={outputRef} style={{ fontSize: '120%', marginTop: '.75em', border: '1px solid grey', padding: '.25em', minHeight: '2em' }} />
		</div>
	);
};

export default MathJaxRenderer;
