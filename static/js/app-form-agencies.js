// TODO davepeck: HACK HACK. You'll notice a bunch of uses of jQuery 
// browser detection in here. That's because this fading stuff
// just isn't working in MSIE, and we're launching in < 24 hours.
// Rather than fix it right, I'm just turning it off for IE entirely.
// 
// Using browser detection (jQuery or otherwise) is evil, bad, and 
// should not be necessary -- but this is a good pragmatic solution for now.

$(document).ready(function() 
{ 
    //make sure public dropdown selected appropriately
    $("#agency_list").tablesorter({ sortList: [[6,0],[5,0]] });

    if (!$.browser.msie)
    {
        $("#list-panel").fadeTo(0, 0.33);
    }
    updateUI();
    
    $("#id_gtfs_choice_0").click(updateUI);
    $("#id_gtfs_choice_1").click(updateUI);
    $("#id_gtfs_choice_2").click(updateUI);
}); 

function updateFilters()
{
    var pd = jQuery("#public_filter option:selected").val();
    var location = jQuery("#location_filter option:selected").val();
    document.location = (location + '?public=' + pd)
}

function updateUI() 
{
    if ($.browser.msie)
    {
        return;
    }
    
    if ($("#id_gtfs_choice_1").is(":checked"))
    {
        $(":checkbox").attr("disabled", false);
        $("#list-panel").fadeTo(500, 1.00);
    }
    else
    {
		$(":checkbox").attr("disabled", true);	
        $("#list-panel").fadeTo(500, 0.33);
	}
}

function updateFilters()
{
    var pd = jQuery("#public_filter option:selected").val();
    var location = jQuery("#location_filter option:selected").val();
    
    //show based on filters
    if (pd=="all" && location=="all")
    {
        $("tr").show();
    }
    else 
    {
        $("tr").hide(); //hide everything
        $("#header-row").show(); //show headers
        
        if (pd=="all")
        {
            $("tr").filter("."+location).show();
        }
        else if (location=="all")
        {
            $("tr").filter("."+pd).show();
        }
        else 
        {
            var filter = "tr[class='" + location + " " + pd + "']";
            $(filter).show();
        }
    }
}

function filter(countryCode) 
{
    $("tr").hide();
    $("#header-row").show();
    $("."+countryCode).show();
}

function getDataString()
{
    var data = $(":checkbox:checked").map(function()
    {
        return $(this).attr("id");
    }).get().join(" | ");

    return data;
}

function sendDataString() 
{
	if ($("#id_gtfs_choice_1").eq(0).is(":checked"))
	{
		$("#id_agency_list").eq(0).val(this.getDataString());
	}
    return true;
}

function dbug(str)
{
	$("#dbug").append(str + "<br />");
}

function reconstitute_from_key(key)
{
    $("#" + key).click();
}

function reconstitute_from_keys(keys)
{
    var trimmed = $.trim(keys);
    
    if (trimmed.length > 0)
    {
        var keys = trimmed.split('|')
        $.each(keys, function(i, key)
        {
            reconstitute_from_key($.trim(key));
        });
    }
}