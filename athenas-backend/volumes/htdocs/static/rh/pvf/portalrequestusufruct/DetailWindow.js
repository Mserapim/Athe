Ext._define('rh.pvf.portalrequestusufruct.DetailWindow', {
    extend: 'rh.pvf.portalrequest.DetailWindow',
    rest: 'rh.pvf.portalrequestusufruct.Restful',


    getFieldSet:function(cfg){
        return this.getBookedUsufructsFieldSet(cfg)
    },


    getBookedUsufructsFieldSet: function (cfg) {
        if (!this._marked)
            this._marked = Ext._create('Ext.form.FieldSet', {
                title: 'Programações',
                items: [
                    this.getBookedUsufructGrid(cfg)
                ]
            });

        return this._marked;
    },

    getBookedUsufructGrid: function (cfg) {
        prev_competence_paid = cfg.group_dgp?'prev_competence_paid':''
        payment = cfg.group_dgp?'payment':''
        if (!this._bookedUsufructGrid) {
            this._bookedUsufructGrid = Ext._create('rh.pvf.portalusufruct.Grid', {
                region: 'south',
                gridAutoLoad: false,
                height: 150,
                columnAction: false,
                columnLines: true,
                configOrderToolBar: [payment],
                onlyColumns: ['start_date', 'end_date', 'days','type_activity',prev_competence_paid],
                canceledsFilterMenu:[],
                doubleClickHandler: function () {}
            });
            this._bookedUsufructGrid.setSortProperty('start_date','ASC',false);
            this._bookedUsufructGrid.setFilterProperty('activity__activity_requests__id', cfg.data.pk, 1000);


        }
        return this._bookedUsufructGrid;
    },

    
    

});