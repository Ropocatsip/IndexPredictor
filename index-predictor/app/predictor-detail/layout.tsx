import Header from "./components/header";

export default function PredictorDetail({ children }: { children: React.ReactNode }) {
  return (
    <div className="">
        <Header/>
        {children}
    </div>
  );
}