Ext._define('corregedoria.prontuary.functionalperformance.listcumulation.Grid', {
    extend: 'core.RestfulGrid', 

    rest: 'corregedoria.prontuary.functionalperformance.listcumulation.Restful',

    configOrderToolBar: ['add', 'remove', 'reload', 'search', ],

    getReloadAction: function() {
        if(!this._reloadAction){
            this._reloadAction = new Ext.Button({
                xtype: 'button',
                scope: this,
                text: 'Atualizar lista de atuações simultâneas',
                iconCls: 'icon-crgmpe icon-crgmpe-reload',
                handler: function() {
                    var mask = new Ext.LoadMask(this.getEl(), {msg: 'Atualizando dados de exercícios simultâneos...'});
                    Ext.Msg.show({
                        title: 'Desempenho Funcional - Cumulações - Prontuário Individual',
                        msg: 'Tem certeza que deseja atualizar períodos de designações simultâneas?',
                        icon: Ext.Msg.QUESTION,
                        buttons: Ext.Msg.YESNO,
                        scope: this,
                        fn: function(btn) {
                            if(btn=='no') return;
                            mask.show();
                            Ext.Ajax.request({
                                scope: this,
                                url: core.callAction('PRONTUARYListCumulation', 'reload'),
                                callback: function() {
                                    mask.hide();
                                },
                                success: function(request) {
                                    var rst = Ext.decode(request.responseText);
                                    if (rst.success == true) {
                                        Ext.Msg.show({
                                            title: 'Desempenho Funcional - Cumulações - Prontuário Individual',
                                            msg: rst.message,
                                            icon: Ext.Msg.INFO,
                                            buttons: Ext.Msg.OK
                                        });
                                        this.getStore().reload();
                                    } else {
                                        Ext.Msg.show({
                                            title: 'Desempenho Funcional - Cumulações - Prontuário Individual',
                                            msg: rst.message,
                                            icon: Ext.Msg.ERROR,
                                            buttons: Ext.Msg.OK
                                        });
                                    }
                                },
                                failure: function(request) {
                                    var rst = Ext.decode(request.responseText);
                                    Ext.Msg.show({
                                        title: 'Desempenho Funcional - Cumulações - Prontuário Individual',
                                        msg: rst.message,
                                        icon: Ext.Msg.ERROR,
                                        buttons: Ext.Msg.OK
                                    });
                                },
                                params: {'prontuary': this.params.prontuary, },
                            });
                        }
                    });
                }
            });
        }
        return this._reloadAction;
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'icons', width: 50, renderer: core.rendererIconGrid, menuDisabled: true, },
                    {header: 'Data de Início', dataIndex: 'cumulation_date_initial', width: 120, align: 'center', },
                    {header: 'Data de Término', dataIndex: 'cumulation_date_final', width: 120, align: 'center', },
                    {header: 'Total de Dias', dataIndex: 'total_days', id: 'autoExpandColumn', align: 'center', },
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.prontuary.functionalperformance.listcumulation.Restful',
    'corregedoria.prontuary.functionalperformance.listcumulation.Grid'
);
