// app/api/ndvi/route.ts
import { NextResponse } from "next/server";
import clientPromise from "../../lib/mongodb";

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url);
    const xAxisParam = searchParams.get("xAxis");
    const yAxisParam = searchParams.get("yAxis");

    const client = await clientPromise;
    const db = client.db("IndexPredictor");
    const collection = db.collection("ndmi");

    if (!xAxisParam && !yAxisParam) {
      const docs = await collection.find({}).toArray();
      return NextResponse.json(docs);
    }

    const xAxis = Number(xAxisParam);
    const yAxis = Number(yAxisParam);

    if (isNaN(xAxis) || isNaN(yAxis)) {
      return NextResponse.json(
        { error: "xAxis and yAxis must be numbers" },
        { status: 400 }
      );
    }

    const doc = await collection.findOne({ xAxis, yAxis });

    if (!doc) {
      return NextResponse.json({ message: "Not found" }, { status: 404 });
    }

    return NextResponse.json(doc);
  } catch (err) {
    console.error(err);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
