import { describe, expect, it } from "vitest";
import { getHeatmapColor, getProjectCountTier } from "./mapStyles";

describe("getProjectCountTier",()=>{
  it.each([[0,"none"],[1,"veryLow"],[5,"low"],[20,"medium"],[50,"high"],[100,"veryHigh"]] as const)("maps %i to %s", (count,tier)=>{
    expect(getProjectCountTier(count)).toBe(tier);
  });
});
describe("getHeatmapColor",()=>{
  it("clamps values to the heatmap range",()=>{
    expect(getHeatmapColor(0,100)).toBe("rgb(37,99,235)");
    expect(getHeatmapColor(100,100)).toBe("rgb(239,68,68)");
    expect(getHeatmapColor(200,100)).toBe("rgb(239,68,68)");
  });
});