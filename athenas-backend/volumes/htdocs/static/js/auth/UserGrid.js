/**
 *
 **/
Ext._define('auth.UserGrid', {
    'extend': 'core.RestfulGrid',

    'restWindow': 'auth.UserWindow',

    keywordFieldMessage: 'Nome, matrícula, email, cpf.',

    renderBoolean: function(field, rest) {
        return function(value, cell, data) {
            return '<div>' + (value ? 'Sim': 'Não') + '</div>';
        };
    },

    toggleFor: function(state, action) {
        var pkset = this.getSelectionModel().getSelections().map(function(data) {
            return data.get('pk');
        });
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Processando...'});

        mask.show();
        rest.doRequest(
            rest.getRoute(
                action,
                false,
                'PUT',
                {
                    scope: this,
                    params: {
                        pk__in: pkset,
                        is_active: (state ? 'on': 'off')
                    },
                    callback: function() {
                        mask.hide();
                        mask = null;
                    },
                    success: function(xhr) {
                        var rst = Ext.decode(xhr.responseText);

                        if(rst.success)
                            this.getStore().reload();
                        else
                            Ext.Msg.show({
                                title: 'Ativando',
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK,
                                msg: rst.message
                            });
                    },
                    failure: function(xhr) {
                        Ext.Msg.show({
                            title: 'Ativando',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: 'Recurso indisponível no momento.'
                        });
                    }
                }
            )
        );
    },

    toggleActive: function(btn, state) {
        this.toggleFor(state, 'toggle_active');
    },

    toggleStaff: function(btn, state) {
        this.toggleFor(state, 'toggle_staff');
    },
    toggleRoot: function(btn, state) {
        this.toggleFor(state, 'toggle_superuser');
    },

    toggleState: function(state) {
        this._filterState = core.nullValue(this._filterState, {
            is_active: false,
            is_inactive: false,
            is_staff: false,
            is_superuser: false
        });

        if(state == 1) this._filterState.is_active = !this._filterState.is_active;
        else if(state == 2) this._filterState.is_staff = !this._filterState.is_staff;
        else if(state == 3) this._filterState.is_superuser = !this._filterState.is_superuser;
        else if(state == 4) this._filterState.is_inactive = !this._filterState.is_inactive;

        if(this._filterState.is_active)
            this.setFilterProperty('is_active', 'on', 101, false);
        else
            this.removeFilterProperty('is_active', 101, false);

        if(this._filterState.is_inactive)
            this.setFilterProperty('is_active', 'off', 104, false);
        else
            this.removeFilterProperty('is_active', 104, false);

        if(this._filterState.is_staff)
            this.setFilterProperty('is_staff', 'on', 102, false);
        else
            this.removeFilterProperty('is_staff', 102, false);

        if(this._filterState.is_superuser)
            this.setFilterProperty('is_superuser', 'on', 103, false);
        else
            this.removeFilterProperty('is_superuser', 103, false);

        this.getStore().reload();
    },

    getFilterMenu: function() {
        if(!this._filterMenu)
            this._filterMenu = [
                {
                    text: 'Mostra somente ativo',
                    checked: false,
                    scope: this,
                    hideOnClick: false,
                    handler: function() { this.toggleState(1); }
                },
                {
                    text: 'Mostra somente inativo',
                    checked: false,
                    scope: this,
                    hideOnClick: false,
                    handler: function() { this.toggleState(4); }
                },
                {
                    text: 'Mostra somente Staff',
                    checked: false,
                    scope: this,
                    hideOnClick: false,
                    handler: function() { this.toggleState(2); }
                },
                {
                    text: 'Mostra somente Root',
                    checked: false,
                    scope: this,
                    hideOnClick: false,
                    handler: function() { this.toggleState(3); }
                }
            ];

        return this._filterMenu;
    },

    getToggleActiveAction: function() {
        if(!this._toggleActiveAction)
            this._toggleActiveAction = Ext._create('Ext.Button', {
                tooltip: 'Ativo',
                iconCls: 'icon-core icon-core-success',
                enableToggle: true,
                scope: this,
                toggleHandler: this.toggleActive
            });

        return this._toggleActiveAction;
    },

    getEmployeeAction: function() {
        if(!this._employeeAction)
            this._employeeAction = Ext._create('Ext.Button', {
                text: 'Empregado',
                iconCls: 'icon-core icon-core-set-employee',
                scope: this,
                handler: this.openEmployeeSetWindow
            });

        return this._employeeAction;
    },

    openEmployeeSetWindow: function() {
        var selected = this.getSelectionModel().getSelected();
        var rest, mask;

        if(selected) {
            Ext._create('auth.UserEmployeeWindow', {
                modal: true,
                params: {
                    user: selected.get('pk')
                },
                values: {
                    employee: selected.get('servidor'),
                    username: selected.get('username')
                },
                callback: {
                    scope: this,
                    fn: function() {
                        this.getStore().reload();
                    }
                }
            }).show();
        }
        else
            Ext.Msg.show({
                title: 'Manipular empregado',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um item para executar esta funcionalidade.'
            });
    },

    getToggleStaffAction: function() {
        if(!this._toggleStaffAction)
            this._toggleStaffAction = Ext._create('Ext.Button', {
                tooltip: 'Equipe',
                iconCls: 'icon-core icon-core-users',
                enableToggle: true,
                scope: this,
                toggleHandler: this.toggleStaff
            });

        return this._toggleStaffAction;
    },

    getToggleRootAction: function() {
        if(!this._toggleRootAction)
            this._toggleRootAction = Ext._create('Ext.Button', {
                tooltip: 'Administrador',
                iconCls: 'icon-core icon-core-admin',
                enableToggle: true,
                scope: this,
                toggleHandler: this.toggleRoot
            });

        return this._toggleRootAction;
    },

    rendererHasEmployeeActive: function(value, cell, data) {
        var style = '';

        if(!data.get('servidor_ativo'))
            style += 'text-decoration:line-through';

        return '<div style="' + style + '">' + value + '</div>';
    },

    rendererHasEmployeeNumberActive: function(value, cell, data) {
        var style = ['text-align:right'];

        if(!data.get('servidor_ativo'))
            style.push('text-decoration:line-through');

        return '<div style="' + style.join(';') + '">' + value + '</div>';
    },

    getCleanupAction: function() {
        if(!this._cleanAction)
            this._cleanAction = Ext._create('Ext.Button', {
                text: 'Limpar Menu',
                iconCls: 'icon-core icon-core-clear',
                scope: this,
                handler: this.cleanupUserMenu
            });

        return this._cleanAction;
    },

    cleanupUserMenu: function() {
        var pkset = this.getSelectionModel().getSelections().map(function(data) {
            return data.get('pk');
        });
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Processando...'});

        if(pkset.length > 0){
            mask.show();
            rest.doRequest(
                rest.getRoute(
                    'cleanup',
                    false,
                    'PUT',
                    {
                        scope: this,
                        params: {
                            pk__in: pkset
                        },
                        callback: function() {
                            mask.hide();
                            mask = null;
                        },
                        success: function(xhr) {
                            var rst = Ext.decode(xhr.responseText);

                            if(rst.success)
                                this.getStore().reload();
                            else
                                Ext.Msg.show({
                                    title: 'Limpando Menu',
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK,
                                    msg: rst.message
                                });
                        },
                        failure: function(xhr) {
                            Ext.Msg.show({
                                title: 'Limpando Menu',
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK,
                                msg: 'Recurso indisponível no momento.'
                            });
                        }
                    }
                )
            );
        }else{
            Ext.Msg.show({
                title: 'Limpando Menu',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'É necessário selecionar pelo menos um item para executar esta funcionalidade.'
            });
        }
    },

    getColumnModel: function(){
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer', {dataIndex: 'numberer'}),
                    // {
                    //     'header': '',
                    //     'dataIndex': 'icons',
                    //     'width': 70,
                    //     'menuDisabled': true,
                    //     'renderer': adm.daily.rendererIconGrid
                    // },
                    {
                        header: 'Matricula',
                        dataIndex: 'servidor_matricula',
                        width: 65,
                        renderer: this.rendererHasEmployeeNumberActive
                    },
                    {
                        header: 'Empregado',
                        dataIndex: 'pessoa_nome_real',
                        id: 'autoExpandColumn',
                        renderer: this.rendererHasEmployeeActive
                    },
                    {
                        header: '',
                        dataIndex: 'pk',
                        width: 45,
                        renderer: function(value) { return '<div style="text-align:right">' + value + '</div>';}
                    },
                    {header: 'Usuário', dataIndex: 'username', width: 225},
                    {
                        header: 'Ativo',
                        dataIndex: 'is_active',
                        width: 70,
                        renderer: this.renderBoolean('is_active', 'auth.UserRestful')
                    },
                    {
                        header: 'Staff',
                        dataIndex: 'is_staff',
                        width: 70,
                        renderer: this.renderBoolean('is_staff', 'auth.UserRestful')
                    },
                    {
                        header: 'Root',
                        dataIndex: 'is_superuser',
                        width: 70,
                        renderer: this.renderBoolean('is_superuser', 'auth.UserRestful')
                    }
                ]
            );

        return this._columnModel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                columnAction: false,
                hideItemsToolbar: ['add', 'remove'],
                configOrderToolBar: [
                    'edit',
                    '-',
                    'toggleRoot',
                    ' ',
                    'toggleActive',
                    ' ',
                    'toggleStaff',
                    '-',
                    'employee',
                    '-',
                    'cleanup',
                    '-',
                    'search',
                    '->',
                    'download'
                ],
            }
        );

        this.getSelectionModel().on({
            scope: this,
            selectionchange: function(sm) {
                var selected = sm.getSelected();

                if(selected) {
                    this.getToggleActiveAction()
                        .toggle(
                            selected.get('is_active'),
                            true
                        );

                    this.getToggleStaffAction()
                        .toggle(
                            selected.get('is_staff'),
                            true
                        );

                    this.getToggleRootAction()
                        .toggle(
                            selected.get('is_superuser'),
                            true
                        );
                }
            }
        });

        auth.UserGrid.superclass.constructor.call(this, cfg);
    }
});

core.RestfulGrid.register(
    'auth.UserRestful',
    'auth.UserGrid'
);
