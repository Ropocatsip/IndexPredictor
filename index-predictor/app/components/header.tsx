import Link from "next/link";

export default function Header() 
{
    return (<>
        <header className="header px-5 py-3 text-left">
            <Link href={'/'} style={{ textDecoration: 'none', color: 'white' }}>IndexPredictor</Link>   
        </header>
    </>);
}