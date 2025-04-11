/**
 *
 **/
 Ext._define('cif.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getInformationMember: function() {
        if(!this._informationmember) {
            this._informationmember = Ext._create('cif.controlinformationmember.ControlInformationMemberGrid', {
                region: 'center',
                minHeight: 200,
            });
            this._informationmember.getSelectionModel().on({
                scope: this,
                selectionchange: function(selm) {
                    var selection = selm.getSelections();
                    if(selection.length > 0) {
                        this.setInformationMember(selection[0]);
                    } else {
                        this.setInformationMember(null);
                    }
                }
            });
        }

        return this._informationmember;
    },

    getTeachingGrid: function() {
        if(!this._teaching) {
            this._teaching = Ext._create('cif.teaching.TeachingGrid', {
                iconCls: 'icon-cif icon-cif-book',
                title: 'Docência',
            });

        }

        return this._teaching;
    },

    getAddressGrid: function() {
        if(!this._address) {
            this._address = Ext._create('cif.address.AddressGrid', {
                iconCls: 'icon-cif icon-cif-house',
                title: 'Endereço',
            });
        }
        return this._address;
    },

    getAttachmentGrid: function() {
        if(!this._attachment) {
            this._attachment = Ext._create('cif.attachment.AttachmentGrid', {
                iconCls: 'icon-cif icon-cif-application-pdf',
                title: 'Anexos',
            });
        }
        return this._attachment;
    },

    getPropertyGrid: function() {
        if(!this._properties) {
            this._properties = Ext._create('cif.property.PropertyGrid', {
                iconCls: 'icon-cif icon-cif-money',
                title: 'Bens e Valores',
            });
        }
        return this._properties;
    },

    getDebtsGrid: function() {
        if(!this._debts) {
            this._debts = Ext._create('cif.debtsencumbrances.DebtsEncumbrancesGrid', {
                iconCls: 'icon-cif icon-cif-dollar',
                title: 'Dívidas e Ônus Reais',
            });
        }
        return this._debts;
    },

    setInformationMember: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);
        if(value !== undefined) {
            this._setInformationMember = value;

            if(dispatch)
                this._observeInformationMember();
        }
        return this._setInformationMember;
    },

    _observeInformationMember: function() {
        var value = this.setInformationMember();
        if(value) {
            this.informationId = value.get('pk');
            this.workplace = value.get('workplace');
            this.getTeachingGrid().enable();
            this.getTeachingGrid().setFilterProperty('member', this.informationId);
            this.getTeachingGrid().setParam('member', this.informationId);
            this.getTeachingGrid().idMember = this.informationId;

            this.getAddressGrid().enable();
            this.getAddressGrid().setFilterProperty('member', this.informationId);

            this.getAddressGrid().setParam('member', this.informationId);

            this.getAddressGrid().setParam('person', value.get('person'));
            this.getAddressGrid().person = value.get('person');

            this.getAddressGrid().idMember = this.informationId;
            this.getAddressGrid().defaultValues({
                workplace: this.workplace,
                idMember: this.informationId,
                person: value.get('person')
            });

            this.getPropertyGrid().enable();
            this.getPropertyGrid().setFilterProperty('member', this.informationId);
            this.getPropertyGrid().setParam('member', this.informationId);
            this.getPropertyGrid().idMember = this.informationId;

            this.getAttachmentGrid().enable();
            this.getAttachmentGrid().setFilterProperty('member', this.informationId);
            this.getAttachmentGrid().setParam('member', this.informationId);
            this.getAttachmentGrid().idMember = this.informationId;

            this.getDebtsGrid().enable();
            this.getDebtsGrid().setFilterProperty('member', this.informationId);
            this.getDebtsGrid().setParam('member', this.informationId);
            this.getDebtsGrid().idMember = this.informationId;

        } else {
            this.getTeachingGrid().getStore().removeAll();
            this.getTeachingGrid().disable();

            this.getAddressGrid().getStore().removeAll();
            this.getAddressGrid().disable();

            this.getAttachmentGrid().getStore().removeAll();
            this.getAttachmentGrid().disable();

            this.getPropertyGrid().getStore().removeAll();
            this.getPropertyGrid().disable();

            this.getDebtsGrid().getStore().removeAll();
            this.getDebtsGrid().disable();
        }
    },

   getTabs: function() {
        if(!this._tabPanel)
            this._tabPanel = Ext._create('Ext.TabPanel', {
                region: 'south',
                width: '100%',
                height: 300,
                minHeight: 200,
                split:true,
                border: true,
                activeTab: 0,
                items: [
                    this.getTeachingGrid(),
                    this.getAddressGrid(),
                    this.getAttachmentGrid(),
                    this.getPropertyGrid(),
                    this.getDebtsGrid(),
                ]
            });

        return this._tabPanel;
   },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Informações',
            }
        );

        Ext.apply(
            cfg,
            {
                border: false,
                layout: 'border',
                items: [
                    this.getInformationMember(),
                    {
                        listeners: {
                            scope: this,
                            render: function() {}
                        },
                        region: 'south',
                        layout: 'hbox',
                        minHeight: 150,
                        height: 400,
                        split: true,
                        bodyStyle: {
                            'border-left': 0,
                            'border-right': 0
                        },
                        layoutConfig: {
                            align: 'stretch'
                        },
                        items: [
                            this.getTabs()
                        ]
                    }
                ]
            }
        );

        cif.Manage.superclass.constructor.call(this, cfg);
        this._observeInformationMember();
    }
});
