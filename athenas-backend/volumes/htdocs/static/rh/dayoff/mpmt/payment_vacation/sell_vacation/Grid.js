Ext._define('rh.dayoff.mpmt.payment_vacation.sell_vacation.Grid', {
    extend: 'rh.dayoff.mpmt.payment_vacation.vacation.Grid',

    rest: 'rh.dayoff.mpmt.payment_vacation.sell_vacation.Restful',

    getColumnModel: function () {
        if (!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    { header: 'Cod', dataIndex: 'pk', width: 50, hidden: true },
                    {
                        id: 'icons',
                        dataIndex: 'icons',
                        header: '',
                        width: 120,
                        sortable: false,
                        renderer: toolkit.util.formatStatus,
                        menuDisabled: true
                    },
                    { 
                        header: 'Status',
                        dataIndex: 'status_conference_payment',
                        width: 100,
                        renderer: function(value, meta, record, rowIndex, colIndex, store) {
                            meta.style = 'font-weight:bold; width: 100px; text-overflow: ellipsis; padding: 3px 3px 3px 5px;'
                            return value;
                        }
                    },
                    { header: 'Matrícula' ,dataIndex: 'employee_registry',  width: 60, hidden: true},
                    { header: 'Servidor', dataIndex: 'employee_unicode', id: 'autoExpandColumn' },
                    { header: 'Situação', dataIndex: 'status_display',  width: 80 },
                    { header: 'Tipo Servidor' ,dataIndex: 'employee_type', width: 80 },
                    { header: 'Atividade', dataIndex: 'activity_unicode', width: 200 },
                    { header: 'Status da Atividade', dataIndex: 'activity_label', width: 90 },
                    { header: 'Grupo', dataIndex: 'group_period', width: 150 },
                    { header: 'Início das Férias', dataIndex: 'earliest_date', width: 90, renderer: Ext.util.Format.dateRenderer('d/m/Y') },
                    { header: 'Dias programados', dataIndex: 'days', width: 40 },
                    { header: 'Comp. Pagamento', dataIndex:'competence_paid', width: 100},
                    { header: 'Marcação da escala', dataIndex: 'from_scale_display', width: 90, renderer: function (value) { return (value ? 'SIM' : 'NÃO'); }, hidden: true },
                    { header: 'Criado por', dataIndex: 'created_by_unicode', width: 100,hidden: true },
                    { header: 'Criado em', dataIndex: 'created_at', width: 90,hidden: true, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i') },
                    { header: 'Modificado por', dataIndex: 'modified_by_unicode', width: 100,hidden: true },
                    { header: 'Modificado em', dataIndex: 'modified_at', width: 90,hidden: true, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i') },
                    { header: 'Autorizado por', dataIndex: 'authorized_by_unicode', width: 100,hidden: true },
                    { header: 'Autorizado em', dataIndex: 'authorized_at', width: 90, hidden: true, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i') },
                ]
            );

        return this._columnModel;
    },

    executeAction: function(method, params){
        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action('DAYOFFSellVacation', method),
            params:params,
            success: function(request) {
                var obj = Ext.decode(request.responseText);
                var icon = obj.success == true ? Ext.Msg.INFO : Ext.Msg.ERROR;
                Ext.Msg.show({
                    width:"400px",
                    title: this.title,
                    icon: icon,
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

    observeFilters: function (cfg, valor='default') {      
        this.setFilterProperty('payment_year', this._year, 0, false);
        
        if(this._month){
            this.setFilterProperty('payment_month', this._month, 1, false);
        }else{
            this.removeFilterProperty('payment_month', 1, false);
        }
        
        if (this._employeeType){
            this.setFilterProperty('activity__acquisition_period__employee__tipo__in', this._employeeType, 4, false);
        }
        this.toggleCtrlPayment(valor)
    },

    buscarComboAno: function(cfg){
        return {
            xtype: 'combo',
            store: new Ext.data.JsonStore({
                proxy: new Ext.data.HttpProxy({
                    url: toolkit.util.Normalize.controller_action('DAYOFFSellVacation', 'buscar_lista_anos'),
                    disableCaching: true,
                    method: 'GET'
                }),
                root: 'root',
                fields: ['pk', 'description']
            }),
            displayField: 'description',
            valueFeild: 'pk',
            emptyText: 'Ano para filtro',
            width: 140,
            triggerAction: 'all',
            value: this._today.getFullYear(),
            listeners: {
                scope: this,
                select: function (combo, record) {
                    var store = this.getStore();

                    if (record.get('pk') != 0)
                        this._year = record.get('pk')
                    else
                        this._year = null
                        
                    this.observeFilters(cfg)
                }
            }
        }
    },

});

core.RestfulGrid.register(
    'rh.dayoff.mpmt.payment_vacation.sell_vacation.Restful',
    'rh.dayoff.mpmt.payment_vacation.sell_vacation.Grid'
);
