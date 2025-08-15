import MathRenderer from '../render/MathRender';
import katexrender from '../render/KaTeXComponent';

const Home = () => {
    const inlineMath = 'c = \\pm\\sqrt{a^2 + b^2}';
    const blockMath = '\\int_0^\\infty x^2 dx';

    return (
        <div>
            <h1>KaTeX in Next.js</h1>
            <katexrender texExpression="c = \\pm\\sqrt{a^2 + b^2}" />
            <p>
                Block math:
                {/* <div>
                    <MathRenderer math={blockMath} />
                </div> */}
            </p>
        </div>
    );
};

export default Home;
