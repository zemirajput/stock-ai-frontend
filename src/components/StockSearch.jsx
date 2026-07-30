import { useState } from "react";


function StockSearch(){

const [stock,setStock] = useState("");


const searchStock = () => {

alert(
`Selected Stock: ${stock}`
);

};


return (

<div className="
bg-slate-800
p-6
rounded-xl
mt-8
">


<h2 className="
text-white
text-xl
mb-4
">

Search Stock

</h2>


<div className="flex gap-4">


<input

type="text"

placeholder="Enter stock symbol e.g. AAPL"

value={stock}

onChange={(e)=>setStock(e.target.value)}

className="
flex-1
p-3
rounded-lg
bg-slate-700
text-white
"

/>


<button

onClick={searchStock}

className="
bg-blue-600
px-6
rounded-lg
text-white
"

>

Search

</button>


</div>


</div>

)

}


export default StockSearch;