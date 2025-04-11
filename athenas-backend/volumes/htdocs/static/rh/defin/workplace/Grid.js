 Ext._define('rh.defin.workplace.Grid', {
    extend: 'core.RestfulGrid',

    // restWindow: 'rh.defin.workplace.Window',

    hideActions: ['add','edit','remove','copy', 'download'],

    configOrderToolBar:  ['search',],

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        // Ext.applyIf(
        //     cfg,
        //     {
        //         situationMenuValue: {
        //             'active': {
        //                 name: 'active',
        //                 checked: true,
        //                 value: true,
        //             },
        //             'finished': {
        //                 name: 'finished',
        //                 checked: true,
        //                 value: false,
        //             },
        //         }
        //     }
        // );

        // var values = [];
        // if(cfg.situationMenuValue.active.checked)
        //     values.push(cfg.situationMenuValue.active.value);
        // if(cfg.situationMenuValue.finished.checked)
        //     values.push(cfg.situationMenuValue.finished.value);

        // Ext.applyIf(
        //     cfg,
        //     {
        //         baseParams: [
        //             {
        //                 'property': 'ativo__in',
        //                 'value': values,
        //                 'stage': 0
        //             }
        //         ]
        //     }
        // );
        // this.situationMenuValue = cfg.situationMenuValue;
        rh.defin.workplace.Grid.superclass.constructor.call(this, cfg);
    },

    // filterSituation: function() {
    //     var values = [];
    //     this.getSituationItemsMenu().forEach(
    //         function(item) {
    //             if(item.checked)
    //                 values.push(item.value);
    //         }
    //     );
    //     this.setFilterProperty('ativo__in', values, 1);
    // },

    // getCheckboxActive: function(cfg_window, cfg){
    //     cfg = core.nullValue(cfg, {});
    //     Ext.applyIf(
    //         cfg,
    //         {
    //             name: 'active',
    //             groupMenu: 'situation',
    //             boxLabel: 'ATIVO',
    //             checked: this.situationMenuValue.active.checked,
    //             value: this.situationMenuValue.active.value,
    //             scope: this,
    //             handler: this.filterSituation
    //         }
    //     );
    //     if(this._checkboxActive == undefined)
    //         this._checkboxActive = new Ext.form.Checkbox(cfg);
    //     return this._checkboxActive;
    // },


    // getCheckboxFinished: function(cfg_window, cfg){
    //     cfg = core.nullValue(cfg, {});
    //     Ext.applyIf(
    //         cfg,
    //         {
    //             name: 'finished',
    //             groupMenu: 'situation',
    //             boxLabel: 'INATIVO',
    //             checked: this.situationMenuValue.finished.checked,
    //             value: this.situationMenuValue.finished.value,
    //             scope: this,
    //             handler: this.filterSituation
    //         }
    //     );
    //     if(this._checkboxFinished == undefined)
    //         this._checkboxFinished = new Ext.form.Checkbox(cfg);
    //     return this._checkboxFinished;
    // },

    // getSituationItemsMenu: function(){
    //     if(this._situationItems == undefined){
    //         this._situationItems = [];
    //         this._situationItems.push(this.getCheckboxActive());
    //         this._situationItems.push(this.getCheckboxFinished());
    //     }
    //     return this._situationItems;
    // },

    // getFilterMenu: function() {
    //     return [
    //         {
    //             name: 'situation',
    //             groupMenu: '',
    //             text: 'Situação',
    //             scope: this,
    //             menu: this.getSituationItemsMenu()
    //         },
    //     ];
    // },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Chave', dataIndex: 'pk', width: 90, hidden: true},
                    {
                        header: 'Ativo',
                        dataIndex: 'ativo',
                        menuDisabled: true,
                        width: 40,
                        renderer: toolkit.util.formatIconYesNo,
                        hidden: false
                    },
                    {header: 'Descrição', dataIndex: 'unicode', id: 'autoExpandColumn'},
                    {header: 'Habilita protocolo', dataIndex: 'habilita_protocolo', width: 90, renderer: function(value) { return (value ? 'SIM' : 'NÃO'); }},
                    {header: 'Sigla', dataIndex: 'sigla', width: 70},
                    {header: 'Código CNMP', dataIndex: 'code_cnmp', width: 120, hidden: false},
                ]
            );

        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'rh.defin.workplace.Restful',
    'rh.defin.workplace.Grid'
);
