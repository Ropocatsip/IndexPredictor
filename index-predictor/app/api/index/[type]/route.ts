import clientPromise from "@/app/lib/mongodb";
import { NextResponse } from "next/server";

export async function GET(
    req: Request,
    { params }: { params: Promise<{ type: string }> },
) {
    try {
        const { searchParams } = new URL(req.url);
        const xAxisParam = searchParams.get("xAxis");
        const yAxisParam = searchParams.get("yAxis");
        const xAxis = Number(xAxisParam);
        const yAxis = Number(yAxisParam);

        const {type} = await params;

        const client = await clientPromise;
        const db = client.db("IndexPredictor");
        const collection = db.collection("indexCoordinates");
        if (!xAxisParam && !yAxisParam) {
            const docs = await collection.find({ type }).toArray();
            if (!docs) {
                return NextResponse.json({ message: "Not found" }, { status: 404 });
            }
            return NextResponse.json(docs);
        } else {
            const doc = await collection.findOne({ xAxis, yAxis, type });
            if (!doc) {
                return NextResponse.json({ message: "Not found" }, { status: 404 });
            }
            return NextResponse.json(doc);
        }

    } catch (err) {
        console.error(err);
        return NextResponse.json(
            { error: "Internal server error" },
            { status: 500 }
        );
    }
}