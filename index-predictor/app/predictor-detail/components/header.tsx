import Link from "next/link";

export default function Header() 
{
    return (<>
        <header className="sub-header px-5 py-2 text-left">
            <ul className="nav">
                <li className="nav-item-first px-3">
                    <Link className="nav-link active" href="ndvi">NDVI</Link>
                </li>
                <li className="nav-item px-3">
                    <Link className="nav-link" href="ndmi">NDMI</Link>
                </li>
            </ul>
        </header>
    </>);
}