Ext._define('rh.pvf.waitingapproval.DetailWindow', {

    rest: 'rh.pvf.waitingapproval.Restful',
    extend:'rh.pvf.portalrequest.DetailWindow',


    constructor: function(cfg) {
        this.extend = cfg.data.path_datail_window
        rh.pvf.waitingapproval.DetailWindow.superclass.constructor.call(this, cfg);
    }, 

    // getFieldSet:function(cfg){
    //     var items =rh.pvf.portalrequestusufruct.DetailWindow.superclass
    //     return items
    //     // if(cfg.data.request_type == 1){
    //     //     return this.getBookedUsufructsFieldSet(cfg)
    //     // }else if(cfg.data.request_type == 4){
    //     //     return this.getWorkLoadFieldSet(cfg)
    //     // }else if(cfg.data.request_type == 5){
    //     //     return this.getUsufructsFieldSet(cfg)
    //     // }else if(cfg.data.request_type == 6){
    //     //     this.width = 800
    //     //     this.height= 780
    //     //     return this.getUsufructRetificationFieldSet(cfg)
          
    //     // }
        
    // },


    // getSubstitutePanel: function (cfg) {
    //     if (!this._substitutePanel)
    //         this._substitutePanel = Ext._create('Ext.Panel', {
    //             title: 'Substitutos',
    //             layout:"form",
    //             frame: true,
    //             border: false,
    //             height: 428,
    //             width:650,
    //             items: [

    //                 {
    //                     xtype: 'fieldset',
    //                     title: 'Substitutos',
    //                     layout:"form",
    //                     border: true,
    //                     items:[
    //                         this.getSubstituteFormPanel(cfg)
    //                     ]
    //                 }, 
    //             ]
    //         });

    //     if(cfg.data.has_substitute){
    //         this._substitutePanel.enable();
    //     }else{
    //         this._substitutePanel.disable();
    //     }
       

    //     return this._substitutePanel;
    // },


    // getWorkLoadFieldSet: function (cfg) {
    //     if (!this._marked)
    //         this._marked = Ext._create('Ext.form.FieldSet', {
    //             title: 'Carga Horária',
    //             items: [
    //                 {
    //                     fieldLabel: 'Jornada Atual',
    //                     xtype: 'displayfield',
    //                     value:cfg.data.old_workload+"h"
                        
    //                 },
    //                 {
    //                     fieldLabel: 'Nova Jornada',
    //                     xtype: 'displayfield',
    //                     value:cfg.data.new_workload+"h"
                        
    //                 },
    //                 {
    //                     fieldLabel: 'Data de Início',
    //                     xtype: 'displayfield',
    //                     value: Ext.util.Format.date(cfg.data.date_work_load, 'd/m/Y')
    //                 },
                   
    //             ]
    //         });

    //     return this._marked;
    // },


    // getBookedUsufructsFieldSet: function (cfg) {
    //     if (!this._marked)
    //         this._marked = Ext._create('Ext.form.FieldSet', {
    //             title: 'Programações',
    //             items: [
    //                 this.getBookedUsufructGrid(cfg)
    //             ]
    //         });

    //     return this._marked;
    // },

    

    // getBookedUsufructGrid: function (cfg) {
    //     if (!this._bookedUsufructGrid) {
    //         this._bookedUsufructGrid = Ext._create('rh.pvf.portalusufruct.Grid', {
    //             region: 'south',
    //             gridAutoLoad: false,
    //             height: 150,
    //             columnAction: false,
    //             columnLines: true,
    //             configOrderToolBar: [],
    //             onlyColumns: ['start_date', 'end_date', 'days','type_activity'],
    //             canceledsFilterMenu:[],
    //             doubleClickHandler: function () { }
    //         });
    //         this._bookedUsufructGrid.setFilterProperty('activity__activity_requests__id', cfg.data.pk, 1000);

    //     }
    //     return this._bookedUsufructGrid;
    // },


    // getUsufructsFieldSet:function(cfg){
    //     if (!this._marked)
    //         this._marked = Ext._create('Ext.form.FieldSet', {
    //             title: 'Programação  a ser cancelada',
    //             items: [
    //                 this.getCancelUsufructGrid(cfg)
    //             ]
    //         });

    //     return this._marked;
    // },

    
    // getCancelUsufructGrid: function (cfg) {
    //     if (!this._usufructGrid) {
    //         this._usufructGrid = Ext._create('rh.pvf.portalusufruct.Grid', {
    //             region: 'south',
    //             gridAutoLoad: false,
    //             height: 150,
    //             columnAction: false,
    //             columnLines: true,
    //             configOrderToolBar: [],
    //             onlyColumns:['start_date', 'end_date', 'days','type_activity'],
    //             canceledsFilterMenu:[],
    //             doubleClickHandler: function () { }
    //         });
    //         this._usufructGrid.setFilterProperty('pk', cfg.data.usufruct_cancel, 1000);

    //     }
    //     return this._usufructGrid;
    // },

    // getUsufructRetificationFieldSet: function (cfg) {
    //     if (!this._marked)
    //         this._marked = this.getUsufructRetificationGrid(cfg)
    //     return this._marked;
    // },

    // getUsufructRetificationGrid: function (cfg) {
    //     if (!this._marked)
    //     this._marked = {
    //         layout: 'column',
    //         items: [
    //             {
    //                 columnWidth: .5,
    //                 autoHeight:true,
    //                 layout: 'form',
    //                 xtype: 'fieldset',
    //                 style: {
    //                     'padding-right': '1px'
    //                 },
    //                 items: [
    //                     {
    //                         title: 'Nova programação',
    //                         items:[
    //                             this.getNewUsufructGrid(cfg)
    //                         ]
    //                     }
                       
    //                 ]
    //             }, 
    //             {   
    //                 autoHeight:true,
    //                 columnWidth: .5,
    //                 xtype: 'fieldset',
    //                 layout: 'form',
    //                 style: {
    //                     'padding-left': '1px'
    //                 },
    //                 items: [ 
    //                     {
    //                         title: 'Programação a ser retificada',
    //                         items:[
    //                             this.getRetificationGrid(cfg)
    //                         ]
    //                     }
                        
    //                 ]
    //             }
    //         ]
    //        }
    
    //     return this._marked;
    // },

    // getNewUsufructGrid: function (cfg) {
    //     if (!this._newUsufructGrid) {
    //         this._newUsufructGrid = Ext._create('rh.pvf.portalusufruct.Grid', {
    //             region: 'south',
    //             gridAutoLoad: false,
    //             height: 150,
    //             columnAction: false,
    //             columnLines: true,
    //             configOrderToolBar: [],
    //             onlyColumns:['start_date', 'end_date', 'days','type_activity'],
    //             canceledsFilterMenu:[],
    //             doubleClickHandler: function () { }
    //         });
    //         var keys = this.setNewSellkeys(cfg.data.usufructs_retification)
    //         if (keys.length > 0){
    //             this._newUsufructGrid.setFilterProperty('pk__in',keys,1000,false);
    //         }
                
    //         this._newUsufructGrid.setFilterProperty('activity__activity_requests__id', cfg.data.pk, 1000);
           

    //     }
    //     return this._newUsufructGrid;
    // },

    // setNewSellkeys:function(values){
    //     var sell_key = []
    //     act_sell= 7
    //     values = values.replaceAll("'",'"')
    //     values = JSON.parse(values)
    //     values.forEach(
    //         function(item){
    //           if(item.type_of_activity == act_sell) 
    //             sell_key.push(item.usufructs__pk)
    //         }     
    //     )
    //     return sell_key
    // },

    // setListkeys:function(values){
    //     var list = []
    //     values = values.replaceAll("'",'"')
    //     values = JSON.parse(values)
    //     values.forEach(
    //         function(item){
    //           list.push(item.usufructs__pk)
    //         }     
    //     )
    //     return list
    // },

    // getRetificationGrid: function (cfg) {
    //     if (!this._retificationUsufructGrid) {
    //         this._retificationUsufructGrid = Ext._create('rh.pvf.portalusufruct.Grid', {
    //             region: 'south',
    //             gridAutoLoad: false,
    //             height: 150,
    //             columnAction: false,
    //             columnLines: true,
    //             configOrderToolBar: [],
    //             onlyColumns:['start_date', 'end_date', 'days','type_activity'],
    //             canceledsFilterMenu:[],
    //             doubleClickHandler: function () { }
    //         });
    //         this._retificationUsufructGrid.setFilterProperty('pk__in',this.setListkeys(cfg.data.usufructs_retification),1000);
    //         //this._usufructGrid.setSortProperty('pk','DESC');

    //     }
    //     return this._retificationUsufructGrid;
    // },


    

});
