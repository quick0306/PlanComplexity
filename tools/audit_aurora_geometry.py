"""Independent Shapely oracle for the versioned Aurora physical aperture mask."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shapely.geometry import box, GeometryCollection
from shapely.ops import unary_union
from aurora_svmat_lab.parser import parse_aurora_rtplan
from aurora_svmat_lab.physical_aperture import beam_geometry, CLOSURE_MM, GEOMETRY_TOL_MM


def independent_polygon(cp, beam):
    """Intersect native polygons, then mask narrow geometric Y-band intersections."""
    layers=[]
    boundaries=(beam.leaf_boundaries_mlcx1,beam.leaf_boundaries_mlcx2)
    for values, edges in zip((cp.mlc_x1_positions_mm,cp.mlc_x2_positions_mm),boundaries):
        count=len(edges)-1
        layers.append(unary_union([
            box(values[j],edges[j],values[j+count],edges[j+1])
            for j in range(count) if values[j+count]>values[j]
        ]))
    effective=layers[0].intersection(layers[1]).intersection(
        box(cp.jaw_x[0],cp.jaw_y[0],cp.jaw_x[1],cp.jaw_y[1]))
    low=max(edges[0] for edges in boundaries)
    high=min(edges[-1] for edges in boundaries)
    grid=sorted({low,high}|{x for edges in boundaries for x in edges if low<x<high})
    kept=[]
    for bottom,top in zip(grid,grid[1:]):
        band=effective.intersection(box(cp.jaw_x[0],bottom,cp.jaw_x[1],top)).buffer(0)
        if band.area<=0:
            continue
        height=min(top,cp.jaw_y[1])-max(bottom,cp.jaw_y[0])
        width=band.area/height if height>0 else 0.0
        if width>CLOSURE_MM+GEOMETRY_TOL_MM:
            kept.append(band)
    return unary_union(kept) if kept else GeometryCollection()


def audit(paths, samples_per_beam=12):
    maximum_area_error=maximum_perimeter_error=0.0
    count=0
    for index,path in enumerate(paths,1):
        parsed=parse_aurora_rtplan(path)
        for beam in parsed.beams:
            geometry=beam_geometry(beam)
            length=len(beam.control_points)
            indices=sorted({round(j*(length-1)/max(1,samples_per_beam-1))
                            for j in range(min(length,samples_per_beam))})
            for cp_index in indices:
                polygon=independent_polygon(beam.control_points[cp_index],beam)
                area_error=abs(polygon.area-geometry.areas[cp_index])
                perimeter_error=abs(polygon.length-geometry.perimeters[cp_index])
                maximum_area_error=max(maximum_area_error,area_error)
                maximum_perimeter_error=max(maximum_perimeter_error,perimeter_error)
                if area_error>1e-7 or perimeter_error>1e-7:
                    raise ValueError(f"Polygon disagreement: {path.name}, CP{cp_index}")
                count+=1
        if index%15==0:
            print(f"{index}/{len(paths)} plans",flush=True)
    return dict(plans=len(paths),control_points=count,closure_threshold_mm=CLOSURE_MM,
                max_area_error_mm2=maximum_area_error,
                max_perimeter_error_mm=maximum_perimeter_error,passed=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir",type=Path,required=True)
    parser.add_argument("--output-json",type=Path,required=True)
    parser.add_argument("--samples-per-beam",type=int,default=12)
    args=parser.parse_args()
    if args.samples_per_beam<2:
        parser.error("At least two samples per beam are required.")
    paths=sorted(args.input_dir.rglob("*.dcm"))
    if not paths:
        raise ValueError("No DICOM plans found.")
    report=audit(paths,args.samples_per_beam)
    args.output_json.parent.mkdir(parents=True,exist_ok=True)
    args.output_json.write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report),flush=True)


if __name__=="__main__":
    main()
