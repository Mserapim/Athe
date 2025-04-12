Ext._define('rh.pvf.portalcancelschedule.DetailWindow', {
    extend:'rh.pvf.portalrequest.DetailWindow',

    rest: 'rh.pvf.portalcancelschedule.Restful',

    getFieldSet:function(cfg){
        return this.getUsufructFieldSet(cfg)
    },

    getUsufructFieldSet: function (cfg) {
        if (!this._marked)
            this._marked = Ext._create('Ext.form.FieldSet', {
                title: 'Programação a ser cancelada',
                items: [
                    this.getUsufructGrid(cfg)
                ]
            });

        return this._marked;
    },

    getUsufructGrid: function (cfg) {
        if (!this._usufructGrid) {
            this._usufructGrid = Ext._create('rh.pvf.portalusufruct.Grid', {
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
            this._usufructGrid.setFilterProperty('pk', cfg.data.usufruct_cancel, 1000);

        }
        return this._usufructGrid;
    },

});   