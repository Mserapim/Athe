
Ext._define('cif.address.AddressGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'cif.address.AddressWindow',

    configOrderToolBar: ['blockUnblock', 'add', 'edit', 'remove', 'confirmCheck', '-', 'search',],

    defaultValues: function(values) {
        if(values)
            this._defaultValues = values;

        return this._defaultValues;
    },

    createItem: function(values) {
        if(values instanceof Ext.Button)
            values = {};

        values = Ext.applyIf(
            core.nullValue(values, {}),
            this.defaultValues()
        );

        cif.address.AddressGrid.superclass.createItem.call(this, values);
    },

    updateItem: function(record) {
        this.setParam('workplace', this.defaultValues().workplace);
        cif.address.AddressGrid.superclass.updateItem.call(this, record);
    },

    getConfirmCheckAction: function(cfg) {
        if(!this.actionconfirm)
            this.actionconfirm = Ext._create('Ext.Button', {
                text: 'Confirmar Informação',
                iconCls: 'icon-cif icon-cif-accept',
                scope: this,
                handler: this.confirmAction
            });

        return this.actionconfirm;
    },

    getBlockUnblockAction: function(cfg) {
        if(!this.actionBlockUnblock)
            this.actionBlockUnblock = Ext._create('Ext.Button', {
                text: 'Bloqueio/Desbloqueio',
                iconCls: 'icon-cif icon-cif-manager',
                scope: this,
                // handler: this.confirmAction
                menu: [
                    {
                        text: 'Bloquear Alteração',
                        scope: this,
                        group: 'tipo',
                        filter: 'todos',
                        iconCls: 'icon-cif icon-cif-lock',
                        handler: function() { this.blockUnblockChange(1); }
                    },
                    {
                        text: 'Desbloquear Alteração',
                        scope: this,
                        group: 'tipo',
                        filter: 'todos',
                        iconCls: 'icon-cif icon-cif-unlock',
                        handler: function() { this.blockUnblockChange(2); }
                    },
                ]
            });

        return this.actionBlockUnblock;
    },

    confirmAction: function(){
        var selection = this.getSelectionModel().getSelections();

        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Persistindo dados...'});

        if(selection.length > 0) {
            mask.show();

            rest.doRequest(
                rest.getRoute('confirm_action', false, 'POST', {
                    scope: this,
                    params: {
                        pks: selection.map(function(item) { return item.get('pk') })
                    },
                    callback: function() {
                        mask.hide();
                        mask = undefined;
                    },
                    success: function(xhr) {
                        var rst = Ext.decode(xhr.responseText);

                        if(rst.success) {
                            this.getStore().reload();
                            Ext.Msg.show({
                                title: 'Atenção',
                                icon: Ext.Msg.INFO,
                                buttons: Ext.Msg.OK,
                                msg: rst.message
                            });
                        }
                        else
                            Ext.Msg.show({
                                title: 'Atenção',
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK,
                                msg: rst.message
                            });
                    },
                    failure: function(xhr) {
                        Ext.Msg.show({
                            title: 'Atenção',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: 'Recurso indisponível no momento.'
                        });
                    },
                })
            );
        }
        else Ext.Msg.show({
            'title': 'Atenção',
            'icon': Ext.Msg.ERROR,
            'buttons': Ext.Msg.OK,
            'msg': 'Selecione pelo menos um item.'
        });
    },

    blockUnblockChange: function(param){
        var selection = this.getSelectionModel().getSelections();

        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Persistindo dados...'});

        if(selection.length > 0) {
            mask.show();

            rest.doRequest(
                rest.getRoute('block_unblock_action', false, 'POST', {
                    scope: this,
                    params: {
                        pks: selection.map(function(item) { return item.get('pk') }),
                        action: param
                    },
                    callback: function() {
                        mask.hide();
                        mask = undefined;
                    },
                    success: function(xhr) {
                        var rst = Ext.decode(xhr.responseText);

                        if(rst.success) {
                            this.getStore().reload();
                            Ext.Msg.show({
                                title: 'Atenção',
                                icon: Ext.Msg.INFO,
                                buttons: Ext.Msg.OK,
                                msg: rst.message
                            });
                        }
                        else
                            Ext.Msg.show({
                                title: 'Atenção',
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK,
                                msg: rst.message
                            });
                    },
                    failure: function(xhr) {
                        Ext.Msg.show({
                            title: 'Atenção',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: 'Recurso indisponível no momento.'
                        });
                    },
                })
            );
        }
        else Ext.Msg.show({
            'title': 'Atenção',
            'icon': Ext.Msg.ERROR,
            'buttons': Ext.Msg.OK,
            'msg': 'Selecione pelo menos um item.'
        });
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    // {header: 'Endereço Anterior', dataIndex: 'previus_addres_unicode', id: 'autoExpandColumn', hidden: true},
                    {header: '', dataIndex: 'icons', width: 120, renderer: core.rendererIconGrid},
//                    {header: 'Autorização Residir Fora da Comarca', dataIndex: 'authorization_status', width: 150},
                    {header: 'Data Início Residência', dataIndex: 'start_date', width: 100, renderer: Ext.util.Format.dateRenderer('d/m/Y')},
                    // {header: 'Data Fim Residência', dataIndex: 'end_date', width: 100, renderer: Ext.util.Format.dateRenderer('d/m/Y')},
                    {header: 'Endereço', dataIndex: 'ref_address_unicode', id: 'autoExpandColumn'},
                    {header: 'Referência', dataIndex: 'refperiod_address_unicode', width: 200},
                    {header: 'Criado em', dataIndex: 'created_at', width: 150, renderer: Ext.util.Format.dateRenderer('d/m/Y') , hidden: true},
                    {header: 'Criado por', dataIndex: 'created_by_unicode', width: 150, hidden: true},
                    {header: 'Atualizado em', dataIndex: 'modified_at', width: 150, renderer: Ext.util.Format.dateRenderer('d/m/Y') , hidden: true},
                    {header: 'Modificado por', dataIndex: 'modified_by_unicode', width: 150, hidden: true},
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'cif.address.AddressRestful',
    'cif.address.AddressGrid'
);

