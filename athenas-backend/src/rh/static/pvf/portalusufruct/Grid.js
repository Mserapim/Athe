Ext._define('rh.pvf.portalusufruct.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.pvf.portalusufruct.Window',

    configOrderToolBar: ['payment',"->","download",],

    getColumnModel: function () {
        if (!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    { header: 'Cod', dataIndex: 'pk', width: 50, hidden: true },
                    { header: 'descricao', dataIndex: 'status_display', id: 'autoExpandColumn' },
                    { header: 'Situação', dataIndex: 'status_type', width: 140},
                    { header: 'Programação', dataIndex: 'subtype_usufruct', width: 140},
                    { header: 'Início', dataIndex: 'start_date', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y') },
                    { header: 'Fim', dataIndex: 'end_date', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y') },
                    { header: 'Dias programados/Vendidos', dataIndex: 'days', width: 100 },
                    { header: 'Tipo', dataIndex: 'type_activity', width: 90},
                    { header: 'Previsão de Pagamento', dataIndex:'prev_competence_paid',width: 200},
                    { header: 'Início do período aquisitivo', dataIndex: 'start_date_acquisition', width: 120, renderer: Ext.util.Format.dateRenderer('d/m/Y') },


                ]
            );

        return this._columnModel;
    },

    getPaymentAction: function () {
        return {
            text: 'Alterar Pagamento',
            scope: this,
            handler: function () {
                this.openPaymentWindow('payment', 'Pagamento')
            },
            iconCls: true,
            icon: '/' + global.Context + '/static/rh/images/planoconta-tipo-liquido.png',
        };
    },

    openPaymentWindow: function (actionCustom, title, type_window) {
        //var pas = this.getAcquisitionPeriodGrid().getSelectionModel().getSelected();
        var values = {
            // acquisition_period: pas.get('pk'),
            // booked_days_cache: pas.get('booked_days_cache'),
            // days_not_booked_cache: pas.get('days_not_booked_cache'),
            // days_to_enjoy_cache: pas.get('days_to_enjoy_cache'),
            selected: this.getSelectionModel().getSelected(),
        };
        var _manage = this;

        var selections = this.getSelectionModel().getSelections();
        if (selections.length > 1){
            return Ext.Msg.show({
                title: this.title,
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: "Selecione um usufruto."
            });
        }
        if (selections.length == 1){
            var modifieds = selections.map(function (item) { return item.get('pk'); });

            Ext._create("rh.dayoff.mpmt.activity.PaymentWindow", {
                values: values,
                actionCustom: actionCustom,
                title: title,
                //acquisitionPeriodRestful: this.resourceRestful,
                type_window: type_window,
                usufructModifieds: modifieds,
                vdf:true,
                owner_grid:this,
                externalCallback: _manage.externalCallback,
                selected: selections,
                select: this.getSelectionModel().getSelected(),
            }).show();
        }else{
            return Ext.Msg.show({
                title: this.title,
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: "Selecione um usufruto."
            });
        }

    },

});


core.RestfulGrid.register(
    'rh.pvf.portalusufruct.Restful',
    'rh.pvf.portalusufruct.Grid'
);    