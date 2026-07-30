function ModelCard1({ model, prediction, accuracy, rmse }) {

return (

<div className="
bg-slate-800
rounded-xl
p-6
text-white
shadow-lg
">

<h2 className="
text-xl
font-bold
mb-4
">
{model}
</h2>


<div className="space-y-3">


<div>
<p className="text-gray-400">
Predicted Price
</p>

<p className="text-3xl font-bold">
${prediction}
</p>
</div>



<div>
<p className="text-gray-400">
Accuracy
</p>

<p className="text-green-400 text-xl">
{accuracy}%
</p>
</div>



<div>
<p className="text-gray-400">
RMSE
</p>

<p className="text-blue-400">
{rmse}
</p>
</div>


</div>


</div>

)

}


export default ModelCard1;