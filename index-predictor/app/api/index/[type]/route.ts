import clientPromise from "@/app/lib/mongodb";
import { NextRequest, NextResponse } from "next/server";

type RouteContext = {
  params: Promise<{ type: string }>;
};

export async function GET(
    req: NextRequest,
    context: RouteContext,
) {
    try {
        const { searchParams } = new URL(req.url);
        const xAxisParam = searchParams.get("xAxis");
        const yAxisParam = searchParams.get("yAxis");
        const xAxis = Number(xAxisParam);
        const yAxis = Number(yAxisParam);

        const { type } = await context.params;
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

export async function POST(
    req: NextRequest,
    context: RouteContext,
) {
    const body = await req.json();
    
    const { row, column } = body;
    const { type } = await context.params;
    
    const client = await clientPromise;
    const db = client.db("IndexPredictor");
    const collection = db.collection("indexCoordinates");
    
    if (row != null && column != null) {
        const xAxis = Number(row);
        const yAxis = Number(column);
        const top = Math.round(1 + (xAxis/4));
        const left = Math.round((592+(13*yAxis))/62);
        const newdata = {
            xAxis,
            yAxis,
            top,
            left,
            type
        };

        const index = await collection.findOne({xAxis, yAxis, type}); 
        if (index) {
            return NextResponse.json(
            { error: `row and column ${xAxis}, ${yAxis} are existed.` },
            { status: 409 }
        );
        } else {
            await collection.insertOne(newdata); 
            const resp = await fetch(`${process.env.FLASK_INTERNAL_URL}/coordinates/${type}/${xAxis}/${yAxis}`,
                {
                    method: "POST",
                    cache: "no-store",
                }
            );
            if (!resp.ok) {
                return NextResponse.json(
                    { error: `Flask call failed for ${type}`, status: resp.status },
                    { status: 502 }
                );
            } else {
                return NextResponse.json({ ok: true, data: newdata }, { status: 201 });
            }
        }
    } else {
        return NextResponse.json(
            { error: "row and column are required." },
            { status: 500 }
        );
    }
}

export async function DELETE(
    req: NextRequest,
    context: RouteContext,
){
    const body = await req.json();
    
    const { row, column } = body;
    const { type } = await context.params;
    
    const client = await clientPromise;
    const db = client.db("IndexPredictor");
    const collection = db.collection("indexCoordinates");
    
    if (row != null && column != null) {
        const yAxis = Number(column);
        const xAxis = Number(row);
        const filter = {
            xAxis, 
            yAxis, 
            type
        };
        const index = await collection.findOne(filter); 
        if (index) {
            await collection.deleteOne(filter); 
            return NextResponse.json({ status: 204 });
        } else {
            return NextResponse.json(
            { error: `no coordinates (${xAxis}, ${yAxis})` },
            { status: 500 }
        );
        }
    } else {
        return NextResponse.json(
            { error: "row and column are required." },
            { status: 500 }
        );
    }
}
