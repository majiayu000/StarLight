import Document, { Html, Head, Main, NextScript } from 'next/document';

class MyDocument extends Document {
    render() {
        return (
            <Html>
                <Head>
                    <link
                        rel="stylesheet"
                        href="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/katex.min.css"
                        integrity="sha384-wcIxkf4k558AjM3Yz3BBFQUbk/zgIYC2R0QpeeYb+TwlBVMrlgLqwRjRtGZiK7ww"
                        crossOrigin="anonymous"
                    />
                    <script
                        defer
                        src="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/katex.min.js"
                        integrity="sha384-hIoBPJpTUs74ddyc4bFZSM1TVlQDA60VBbJS0oA934VSz82sBx1X7kSx2ATBDIyd"
                        crossOrigin="anonymous"
                    ></script>
                    <script
                        defer
                        src="https://cdn.jsdelivr.net/npm/katex@0.16.10/dist/contrib/auto-render.min.js"
                        integrity="sha384-43gviWU0YVjaDtb/GhzOouOXtZMP/7XUzwPTstBeZFe/+rCMvRwr4yROQP43s0Xk"
                        crossOrigin="anonymous"
                    ></script>
                </Head>
                <body>
                    <Main />
                    <NextScript />
                    <script>
                        {`
              document.addEventListener("DOMContentLoaded", function() {
                renderMathInElement(document.body, {
                  delimiters: [
                    {left: '$$', right: '$$', display: true},
                    {left: '$', right: '$', display: false},
                    {left: '\\(', right: '\\)', display: false},
                    {left: '\\[', right: '\\]', display: true}
                  ],
                  throwOnError: false
                });
              });
            `}
                    </script>
                </body>
            </Html>
        );
    }
}

export default MyDocument;
