import KatexSpan from './katex'

// Text taken from https://en.wikipedia.org/wiki/Quadratic_formula
const quadraticEquationTest = `你撒的舒适度是\frac{\frac{1}{x}+\frac{1}{y}}{y-z}`;

export default async function WithoutKatexPage() {
    return (
        <main className='bg-slate-300 w-[100dvw] h-[100dvh] flex justify-center items-center'>
            <div className='bg-slate-200 max-w-screen-sm flex justify-center items-center'>
                <KatexSpan
                    text={quadraticEquationTest}
                    className='mx-20 my-20 text-xl'
                />

            </div>
        </main>
    );
}