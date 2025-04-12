 Ext._define('rh.gratifications_manager.cumulative_exercises_permanent.consolidado.Grid', {
    extend: 'core.RestfulGrid',

    rest: 'rh.gratifications_manager.cumulative_exercises_permanent.consolidado.Restful',

    restWindow: 'rh.gratifications_manager.cumulative_exercises_permanent.consolidado.Window',

    hideItemsToolbar: ['add','edit','remove','download'],
    hideActions: ['remove', 'copy', 'edit'],

    configOrderToolBar: ['search','->'],

    getColumnModel: function(){
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Chave', dataIndex: 'pk', width: 55, hidden: true},
                    {header: '', dataIndex: 'icons', width: 45, menuDisabled: true, renderer: toolkit.util.formatStatus },
                    {header: 'Servidor', dataIndex: 'servidor_unicode', width: 150, id: 'autoExpandColumn'},
                    {header: 'Qtd Dias Afastamento', dataIndex: 'qtd_dias_afastamento', width: 120},
                    {header: 'Qtd Dias Consolidado', dataIndex: 'qtd_dias_consolidado', width: 120},
                    {header: 'Qtd Dias Deferido', dataIndex: 'qtd_dias_deferido', width: 120},
                    {header: '% Consolidado', dataIndex: 'pct_consolidado', width: 100},
                    {header: '% Deferido', dataIndex: 'pct_deferido', width: 100},
                ]
            );

        return this._columnModel;
    },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            gridAutoLoad: false,
        });

        rh.gratifications_manager.cumulative_exercises_permanent.consolidado.Grid.superclass.constructor.call(this, cfg);
        this.setFilterProperty('status__in', ['AVAL']);
    },

    setParamsFilterMenu: function(chk, option){
        this._setParamsFilterMenu = core.nullValue(this._setParamsFilterMenu, ['AVAL']);
        if(!chk.checked)
            this._setParamsFilterMenu.push(option)
        else
            this._setParamsFilterMenu.remove(option)

        this.setFilterProperty('status__in', this._setParamsFilterMenu);
    },

    getFilterMenu: function(){
        this._getFilterMenu = [
            {
                text: 'Avaliar',
                checked: true,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.setParamsFilterMenu(chk, 'AVAL') },
            },
            {
                text: 'Deferido',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.setParamsFilterMenu(chk, 'DEFER') },
            },
            {
                text: 'Indeferido',
                checked: false,
                scope: this,
                hideOnClick: false,
                handler: function(chk) { this.setParamsFilterMenu(chk, 'INDEFER') },
            }
        ];

        return this._getFilterMenu
    },

    _realizarReq: function(params, nome_classe, nome_metodo){
        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action(nome_classe,nome_metodo),
            params: params,
            success: function(request) {
                var obj = Ext.decode(request.responseText);
                Ext.Msg.show({
                    width:"400px",
                    title: this.title,
                    icon: Ext.Msg.INFO,
                    buttons: Ext.Msg.OK,
                    msg: obj.message
                });
                if(obj.success == true){ this.getStore().reload(); }
            },
            failure: function() {
                Ext.Msg.show({
                    title: this.title,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Recurso indisponivel no momento, tente novamente mais tarde.'
                });
            },
            scope: this
        });
    },

    _DeferirCumul: function(exerc_cumul_perm){
        if(exerc_cumul_perm.status == 'Indeferido'){
            var msg = 'O registro selecionado está INDEFERIDO, tem certeza que deseja deferir?';
        }else{
            var msg = 'Tem certeza que deseja deferir o registro selecionado?';
        }
        Ext.Msg.show({
            msg: msg,
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function (b) {
                if (b == 'no') return;

                var params = { exerc_cumul_perm_id: exerc_cumul_perm.pk };
                this._realizarReq(params, 'GMExercCumulPermanenteConsolidado', 'deferir_exerc_cumul_perm');
            }
        });
    },

    _IndeferirCumul: function(exerc_cumul_perm_id){
        Ext.Msg.show({
            msg: 'Tem certeza que deseja indeferir o registro selecionado?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function (b) {
                if (b == 'no') return;

                var params = { exerc_cumul_perm_id: exerc_cumul_perm_id };
                this._realizarReq(params, 'GMExercCumulPermanenteConsolidado', 'indeferir_exerc_cumul_perm');
            }
        });
    },

    getConfigCustomActions: function(){
        return [
            {
                iconCls: 'icon-16px icon-fopag icon-compile',
                tooltip: 'Deferir',
                scope: this,
                handler: function(action, index){ this._DeferirCumul(action._store.getAt(index).data) },
            },
            {
                iconCls: 'icon-16px icon-core icon-core-delete',
                tooltip: 'Indeferir',
                scope: this,
                handler: function(action, index){ this._IndeferirCumul(action._store.getAt(index).data.pk) },
            },
        ];
    },

});

core.RestfulGrid.register(
    'rh.gratifications_manager.cumulative_exercises_permanent.consolidado.Restful',
    'rh.gratifications_manager.cumulative_exercises_permanent.consolidado.Grid'
);
