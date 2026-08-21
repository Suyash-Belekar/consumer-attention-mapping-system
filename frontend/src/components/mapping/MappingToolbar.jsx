import React from "react";
import "./MappingToolbar.css";
const TOOLS=[["select","Select"],["shelf","Draw shelf"],["tier","Draw tier"],["product","Map product"],["tracking","Tracking"]];
export default function MappingToolbar({mode,onModeChange}){return <div className="mapping-toolbar">{TOOLS.map(([v,l])=><button key={v} className={mode===v?"active":""} onClick={()=>onModeChange(v)}>{l}</button>)}<span/><button>Sync views</button><button>Undo</button></div>;}