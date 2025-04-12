Ext._define('rh.pvf.portalretificationschedule.DetailWindow', {
    extend:'rh.pvf.portalrequest.DetailWindow',

    rest: 'rh.pvf.portalretificationschedule.Restful',

    width: 920,
    
    height: 800,

    getFieldSet:function(cfg){
        return this.getUsufructFieldSet(cfg) 
    },

    getUsufructFieldSet: function (cfg) {
        if (!this._marked)
        this._marked = {
            layout: 'column',
            items: [
                {
                    columnWidth: .49,
                    autoHeight:true,
                    layout: 'form',
                    xtype: 'fieldset',
                    style: {
                        'padding-right': '1px'
                    },
                    items: [
                        {
                            title: 'Nova programação',
                            items:[
                                this.getNewUsufructGrid(cfg)
                            ]
                        }
                       
                    ]
                }, 
                {   
                    autoHeight:true,
                    columnWidth: .49,
                    xtype: 'fieldset',
                    layout: 'form',
                    style: {
                        'padding-left': '1px'
                    },
                    items: [ 
                        {
                            title: 'Programação a ser retificada',
                            items:[
                                this.getRetificationUsufructGrid(cfg)
                            ]
                        }
                        
                    ]
                }
            ]
           }
    
        return this._marked;
    },

    getNewUsufructGrid: function (cfg) {
        if (!this._newUsufructGrid) {
            this._newUsufructGrid = Ext._create('rh.pvf.portalusufruct.Grid', {
                region: 'south',
                gridAutoLoad: false,
                height: 150,
                columnAction: false,
                columnLines: true,
                configOrderToolBar: [],
                onlyColumns:['start_date', 'end_date', 'days','type_activity'],
                canceledsFilterMenu:[],
                doubleClickHandler: function () { }
            });
            // var keys = this.setNewSellkeys(cfg.data.usufructs_retification)
            // if (keys.length > 0){
            //     this._newUsufructGrid.setFilterProperty('pk__in',keys,1000,false);
            // }
            this._newUsufructGrid.setSortProperty('start_date','ASC',false)
            this._newUsufructGrid.setFilterProperty('activity__activity_requests__id', cfg.data.pk, 1000);
            this._newUsufructGrid.setFilterProperty('status__in',[1,4,4096,1024],1001);

           

        }
        return this._newUsufructGrid;
    },

    setNewSellkeys:function(values){
        var sell_key = []
        act_sell= 7
        values = values.replaceAll("'",'"')
        values = JSON.parse(values)
        values.forEach(
            function(item){
              if(item.type_of_activity == act_sell) 
                sell_key.push(item.usufructs__pk)
            }     
        )
        return sell_key
    },

    setListkeys:function(values){
        var list = []
        values = values.replaceAll("'",'"')
        values = JSON.parse(values)
        values.forEach(
            function(item){
              list.push(item)
            }     
        )
        return list
    },

    getRetificationUsufructGrid: function (cfg) {
        if (!this._retificationUsufructGrid) {
            this._retificationUsufructGrid = Ext._create('rh.pvf.portalusufruct.Grid', {
                region: 'south',
                gridAutoLoad: false,
                height: 150,
                columnAction: false,
                columnLines: true,
                configOrderToolBar: [],
                onlyColumns:['start_date', 'end_date', 'days','type_activity'],
                canceledsFilterMenu:[],
                doubleClickHandler: function () { }
            });
            this._retificationUsufructGrid.setSortProperty('start_date','ASC',false)
            this._retificationUsufructGrid.setFilterProperty('pk__in',this.setListkeys(cfg.data.usufructs_retification),1000);
            //this._retificationUsufructGrid.setFilterProperty('pk__in',cfg.data.usufructs_retification,1000);
            //this._usufructGrid.setSortProperty('pk','DESC');

        }
        return this._retificationUsufructGrid;
    },

});   